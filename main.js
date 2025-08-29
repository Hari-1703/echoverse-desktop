// main.js
require("dotenv").config();
const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs");
const axios = require("axios");
const { ElevenLabsClient } = require("@elevenlabs/elevenlabs-js");

// Initialize ElevenLabs API client
const eleven = new ElevenLabsClient({
  apiKey: process.env.ELEVENLABS_API_KEY,
});

// Create Window
function createWindow() {
  const win = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadFile(path.join(__dirname, "build", "index.html"));
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

// Generate audiobook (Gemini + ElevenLabs API integration)
ipcMain.handle("generate-complete-audiobook", async (event, { prompt, mood, voice }) => {
  const apiKey = process.env.REACT_APP_GEMINI_API_KEY;
  if (!apiKey) throw new Error("Gemini API key not found in .env file.");

  let storyText = "";
  let audioUrl = "";

  // STEP 1: Generate Story with Gemini
  try {
    const fullPrompt = `
      You are an expert audiobook narrator. 
      Write a long, immersive horror story in a ${mood} tone, based on the idea: "${prompt}".
      Rules:
      - The story should be between 600–1000 words (about 3–5 minutes read).
      - Do not include greetings, disclaimers, or instructions.
      - Begin immediately with the story itself.
      - End naturally with a chilling or satisfying conclusion, without commentary.
      - The style must feel vivid, descriptive, and engaging — like a published audiobook.
    `;

    console.log("🔵 Sending request to Gemini API...");
    const response = await axios.post(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=${apiKey}`,
      {
        contents: [{ parts: [{ text: fullPrompt }] }],
      },
      { headers: { "Content-Type": "application/json" } }
    );

    storyText = response.data?.candidates?.[0]?.content?.parts?.[0]?.text || "";
    console.log("✅ Gemini response length:", storyText.length);

    if (!storyText) throw new Error("Gemini returned empty story.");
  } catch (err) {
    console.error("❌ Gemini API error:", err.response?.data || err.message);
    throw new Error("Failed to generate story from Gemini API.");
  }

  // STEP 2: Generate TTS with ElevenLabs
  try {
    console.log("🔵 Sending story to ElevenLabs TTS...");
    const audio = await eleven.textToSpeech.convert(voice || "Rachel", {
      text: storyText,
      model_id: "eleven_multilingual_v2", // Best free human-like voices
    });

    const filename = `audiobook-${Date.now()}.mp3`;
    const filePath = path.join(app.getPath("userData"), filename);

    const buffer = Buffer.from(await audio.arrayBuffer());
    fs.writeFileSync(filePath, buffer);

    audioUrl = `data:audio/mp3;base64,${buffer.toString("base64")}`;
    console.log("✅ ElevenLabs audio generated:", filePath);
  } catch (err) {
    console.error("❌ ElevenLabs API error:", err.message);
    throw new Error("Failed to generate audio from ElevenLabs.");
  }

  return { storyText, audioUrl };
});
