// server/src/services/aiService.ts
import OpenAI from "openai";
import dotenv from "dotenv";

dotenv.config();

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function enrichPrompt(rawPrompt: string) {
  const response = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          "You are LoopLabs AI Assistant. Expand short creative prompts into full cinematic descriptions for video generation — including visual mood, style, tone, transitions, and scene ideas.",
      },
      {
        role: "user",
        content: rawPrompt,
      },
    ],
  });

  return response.choices[0].message?.content?.trim() ?? rawPrompt;
}
