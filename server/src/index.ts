// server/src/index.ts
import Fastify from "fastify";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";
import archiver from "archiver";
import OpenAI from "openai";
import * as dotenv from "dotenv";

dotenv.config();

const fastify = Fastify({ logger: true });
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// --- Simple readiness scoring ---
function calculateReadiness(data: any) {
  let score = 0;
  if (data.prompt) score += 25;
  if (data.media?.length) score += 25;
  if (data.keywords?.length) score += 20;
  if (data.hashtags?.length) score += 15;
  if (data.audio) score += 10;
  if (data.brand) score += 5;
  return Math.min(score, 100);
}

// --- Helper to ZIP job folder ---
async function zipJobFolder(jobDir: string, zipPath: string) {
  return new Promise<void>((resolve, reject) => {
    const output = fs.createWriteStream(zipPath);
    const archive = archiver("zip", { zlib: { level: 9 } });

    output.on("close", () => resolve());
    archive.on("error", (err) => reject(err));

    archive.pipe(output);
    archive.directory(jobDir, false);
    archive.finalize();
  });
}

// --- AI enrichment helper ---
async function enrichPrompt(rawPrompt: string): Promise<string> {
  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content:
            "You are LoopLabs AI Assistant. Expand short creative prompts into cinematic video briefs. Include tone, visuals, camera movement, and vibe. Keep it under 80 words.",
        },
        { role: "user", content: rawPrompt },
      ],
    });

    // Safely extract content with correct typing
    const message = completion.choices?.[0]?.message?.content;
    return message?.trim() ?? rawPrompt;
  } catch (err) {
    console.error("⚠️  OpenAI enrichment failed:", err);
    return rawPrompt;
  }
}

// --- POST /generate ---
fastify.post("/generate", async (req, reply) => {
  const body: any = req.body;
  const text = body.prompt ?? body.text ?? "Default text";
  const theme = body.theme ?? "dark";
  const duration = body.duration ?? 5;

  // --- Enrich prompt using OpenAI ---
  if (body.prompt && process.env.OPENAI_API_KEY) {
    console.log("🤖 Enriching prompt via OpenAI...");
    body.prompt = await enrichPrompt(body.prompt);
    console.log("✅ Enriched prompt:", body.prompt.slice(0, 120) + "...");
  }

  const readiness = calculateReadiness(body);
  const jobId = Date.now();
  const jobDir = path.resolve("../output", `job_${jobId}`);
  fs.mkdirSync(jobDir, { recursive: true });

  // --- Metadata ---
  const metadata = {
    id: jobId,
    timestamp: new Date().toISOString(),
    input: body,
    readiness,
    expectedOutput: path.join(jobDir, `video.mp4`),
  };
  const metaPath = path.join(jobDir, "metadata.json");
  fs.writeFileSync(metaPath, JSON.stringify(metadata, null, 2));

  // --- Python engine call ---
  const enginePath = path.resolve("../engine/main.py");
  const venvPython =
    "/Users/johan/VS Code Repositories/Loop-Labs/looplabs/engine/venv/bin/python3";

  return new Promise((resolve, reject) => {
    const py = spawn(venvPython, [enginePath], {
      cwd: path.resolve("../engine"),
      env: { ...process.env },
    });

    let output = "";
    let error = "";

    py.stdout.on("data", (data) => (output += data.toString()));
    py.stderr.on("data", (data) => (error += data.toString()));

    py.on("close", async (code) => {
      if (code === 0) {
        console.log(`✅ Job ${jobId} done (score: ${readiness}%)`);

        // --- Move generated MP4 ---
        const outputFile = output.match(/\/Users[^\n]+\.mp4/);
        let finalVideoPath = "";
        if (outputFile && outputFile[0]) {
          const source = outputFile[0];
          const dest = path.join(jobDir, "video.mp4");
          try {
            fs.renameSync(source, dest);
            finalVideoPath = dest;
          } catch (err) {
            console.error("Move failed:", err);
          }
        }

        // --- ZIP job folder ---
        const zipPath = path.resolve("../output", `job_${jobId}.zip`);
        try {
          await zipJobFolder(jobDir, zipPath);
          console.log(`📦 Job packaged: ${zipPath}`);
        } catch (err) {
          console.error("Zip failed:", err);
        }

        resolve(
          reply.send({
            success: true,
            readiness,
            jobId,
            folder: jobDir,
            video: finalVideoPath,
            zip: zipPath,
            metadata: metaPath,
          })
        );
      } else {
        console.error(`❌ Job ${jobId} failed:`, error);
        reject(reply.status(500).send({ success: false, error }));
      }
    });

    // Send full JSON payload to Python via stdin
    py.stdin.write(JSON.stringify(body));
    py.stdin.end();
  });
});

// --- Download endpoint ---
fastify.get("/download/:jobId", async (req, reply) => {
  const { jobId } = req.params as { jobId: string };
  const zipPath = path.resolve("../output", `job_${jobId}.zip`);
  if (!fs.existsSync(zipPath)) {
    return reply.status(404).send({ error: "Job not found" });
  }
  reply.header("Content-Disposition", `attachment; filename=job_${jobId}.zip`);
  return reply.send(fs.createReadStream(zipPath));
});

console.log("📁 Download route registered");

// --- Start server ---
fastify.listen({ port: 3000 }, (err, address) => {
  if (err) throw err;
  console.log(`🚀  API running at ${address}`);
});
