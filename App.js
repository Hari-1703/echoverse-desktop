// App.js
import React, { useState, useRef } from "react";

const App = () => {
  const [input, setInput] = useState("");
  const [mood, setMood] = useState("scary");
  const [voice, setVoice] = useState("Rachel");
  const [story, setStory] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const audioRef = useRef(null);

  const generateAudiobook = async () => {
    if (!input.trim()) {
      alert("⚠️ Please enter a story idea!");
      return;
    }

    setIsLoading(true);
    setStory("");
    setAudioUrl("");

    try {
      const result = await window.electronAPI.generateCompleteAudiobook({
        prompt: input,
        mood,
        voice,
      });

      setStory(result.storyText);
      setAudioUrl(result.audioUrl);
    } catch (err) {
      console.error("Detailed Error:", err);
      alert("❌ Failed to generate audiobook. Check API keys and internet.");
    } finally {
      setIsLoading(false);
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>🎧 EchoVerse – AI Horror Audiobooks</h1>

      {/* Input Area */}
      <textarea
        rows="5"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter your horror story idea..."
        style={styles.textarea}
      />

      {/* Controls */}
      <div style={styles.controls}>
        <div>
          <label style={styles.label}>😱 Mood: </label>
          <select value={mood} onChange={(e) => setMood(e.target.value)} style={styles.select}>
            <option value="scary">Scary</option>
            <option value="calm">Calm</option>
            <option value="excited">Excited</option>
            <option value="suspenseful">Suspenseful</option>
          </select>
        </div>

        <div>
          <label style={styles.label}>🎤 Voice: </label>
          <select value={voice} onChange={(e) => setVoice(e.target.value)} style={styles.select}>
            <option value="Rachel">Rachel</option>
            <option value="Bella">Bella</option>
            <option value="Antoni">Antoni</option>
            <option value="Domi">Domi</option>
          </select>
        </div>
      </div>

      {/* Buttons */}
      <div style={styles.buttonGroup}>
        <button onClick={generateAudiobook} disabled={isLoading} style={styles.button}>
          {isLoading ? "⏳ Generating..." : "⚡ Generate Story & Audio"}
        </button>
        {story && (
          <button onClick={generateAudiobook} style={{ ...styles.button, background: "#f39c12" }}>
            🔄 Regenerate Story
          </button>
        )}
      </div>

      {/* Output */}
      {(story || audioUrl) && (
        <div style={styles.card}>
          {story && (
            <div style={styles.storySection}>
              <h2>📖 Horror Story</h2>
              <p style={styles.storyText}>{story}</p>
            </div>
          )}

          {audioUrl && (
            <div style={styles.audioSection}>
              <h2>🔊 Audio Playback</h2>
              <audio ref={audioRef} controls src={audioUrl} style={styles.audioPlayer}></audio>
              <button onClick={stopAudio} style={{ ...styles.button, marginTop: "10px" }}>
                ⏹ Stop
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    fontFamily: "Arial, sans-serif",
    padding: "30px",
    background: "#0f172a",
    color: "#f8fafc",
    minHeight: "100vh",
  },
  header: {
    textAlign: "center",
    fontSize: "2rem",
    marginBottom: "20px",
    color: "#e879f9",
  },
  textarea: {
    width: "100%",
    padding: "15px",
    borderRadius: "12px",
    border: "1px solid #475569",
    marginBottom: "15px",
    fontSize: "1rem",
    background: "#1e293b",
    color: "#f1f5f9",
  },
  controls: {
    display: "flex",
    justifyContent: "space-between",
    marginBottom: "15px",
  },
  label: {
    marginRight: "10px",
    fontWeight: "bold",
  },
  select: {
    padding: "8px",
    borderRadius: "8px",
    border: "1px solid #64748b",
    background: "#1e293b",
    color: "#f8fafc",
  },
  buttonGroup: {
    display: "flex",
    gap: "15px",
    marginBottom: "25px",
  },
  button: {
    padding: "12px 20px",
    borderRadius: "10px",
    border: "none",
    cursor: "pointer",
    fontWeight: "bold",
    background: "linear-gradient(to right, #ec4899, #8b5cf6)",
    color: "#fff",
    transition: "0.3s",
  },
  card: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "20px",
    background: "#1e293b",
    borderRadius: "16px",
    padding: "20px",
    boxShadow: "0 4px 20px rgba(0,0,0,0.4)",
  },
  storySection: {
    overflowY: "auto",
    maxHeight: "400px",
    paddingRight: "10px",
  },
  storyText: {
    lineHeight: "1.6",
    whiteSpace: "pre-wrap",
  },
  audioSection: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  audioPlayer: {
    width: "100%",
    marginTop: "10px",
  },
};

export default App;
