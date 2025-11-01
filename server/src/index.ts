// server/src/index.ts
import Fastify from "fastify";
import { spawn } from "child_process";
import path from "path";

const fastify = Fastify({ logger: true });

// --- POST /generate ---
fastify.post("/generate", async (req, reply) => {
  const body: any = req.body;
  const text = body.text ?? "Default text";
  const theme = body.theme ?? "dark";
  const duration = body.duration ?? 5;

  // --- Path setup ---
  const enginePath = path.resolve("../engine/main.py");
  const venvPython =
    "/Users/johan/VS Code Repositories/Loop-Labs/looplabs/engine/venv/bin/python3";

  // --- Spawn Python process ---
  return new Promise((resolve, reject) => {
    const py = spawn(venvPython, [enginePath], {
      cwd: path.resolve("../engine"),
      env: { ...process.env },
    });

    let output = "";
    let error = "";

    py.stdout.on("data", (data) => (output += data.toString()));
    py.stderr.on("data", (data) => (error += data.toString()));

    py.on("close", (code) => {
      if (code === 0) {
        console.log("✅ Engine completed");
        resolve(reply.send({ success: true, log: output.trim() }));
      } else {
        console.error("❌ Engine error:", error);
        reject(reply.status(500).send({ success: false, error }));
      }
    });

    // Send text to Python stdin
    py.stdin.write(`${text}\n`);
    py.stdin.end();
  });
});

// --- Start server ---
fastify.listen({ port: 3000 }, (err, address) => {
  if (err) throw err;
  console.log(`🚀  API running at ${address}`);
});
