// preload.js

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  getSummary: (prompt) => ipcRenderer.invoke("get-summary", prompt),
  saveAudio: (text) => ipcRenderer.invoke("save-audio", text),
  getAudiobookList: () => ipcRenderer.invoke("get-audiobook-list"),
  playAudioFile: (filename) => ipcRenderer.invoke("play-audio-file", filename),
  generateAudiobook: (data) => ipcRenderer.invoke("generate-audio-book", data),
});
