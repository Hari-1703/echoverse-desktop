require("dotenv").config();
const axios = require("axios");

(async () => {
  try {
    const apiKey = process.env.REACT_APP_GEMINI_API_KEY;
    if (!apiKey) {
      throw new Error("No Gemini API key found in .env");
    }

    console.log("🔑 Gemini Key Loaded:", apiKey.slice(0, 6) + "...");

    const response = await axios.post(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=${apiKey}`,
      {
        contents: [{ parts: [{ text: "Write a very short horror story about a haunted mirror." }] }],
      },
      { headers: { "Content-Type": "application/json" } }
    );

    console.log("✅ Gemini Response:", JSON.stringify(response.data, null, 2));
  } catch (err) {
    console.error("❌ Gemini Error:", err.response?.data || err.message);
  }
})();
