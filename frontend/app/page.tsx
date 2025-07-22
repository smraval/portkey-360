
"use client";
import { useState } from "react";
import dynamic from "next/dynamic";

interface ViewerProps { 
  src: string;
  isLoading?: boolean;
}

const PanoramaViewer = dynamic<ViewerProps>(
  () => import("../components/PanoramaViewer").then((m) => m.default),
  { ssr: false }
);

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [imgSrc, setImgSrc] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [generationTime, setGenerationTime] = useState<number | null>(null);

  async function generate() {
    if (!prompt.trim()) {
      setError("Please enter a prompt");
      return;
    }

    setIsLoading(true);
    setError("");
    setImgSrc("");
    setGenerationTime(null);

    try {
      const startTime = Date.now();
      const res = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Generation failed");
      }

      const data = await res.json();
      setImgSrc(`data:image/png;base64,${data.image_b64}`);
      setGenerationTime(data.generation_time || (Date.now() - startTime) / 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !isLoading) {
      generate();
    }
  };

  return (
    <main className="min-h-screen bg-white text-gray-800">
      <div className="container mx-auto px-6 py-8">
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold mb-4 gradient-title" style={{ fontFamily: 'Apercu, sans-serif' }}>
            portkey360
          </h1>
          {/* <p className="text-xl text-gray-600 max-w-2xl mx-auto" style={{ fontFamily: 'Apercu, sans-serif' }}>
          🪄
          </p> */}
        </div>
        <div className="max-w-4xl mx-auto mb-12">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
            <div className="flex gap-4 mb-6">
              <div className="flex-1 relative">
                <input
                  className="w-full px-6 py-4 text-lg rounded-xl border-2 border-gray-200 focus:border-accent focus:outline-none transition-colors bg-gray-50 focus:bg-white"
                  placeholder="Describe your panoramic vision... (e.g., 'a forest with a river')"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isLoading}
                />
  
              </div>
              <button
                className={`px-8 py-4 rounded-xl text-lg font-medium transition-all duration-200 ${
                  isLoading
                    ? "primary-button"
                    : "primary-button hover:shadow-lg"
                }`}
                onClick={generate}
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="flex items-center gap-3">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Generating...
                  </div>
                ) : (
                  "Generate"
                )}
              </button>
            </div>


            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                <div className="flex items-center gap-2">
                  <span className="text-red-500">⚠</span>
                  {error}
                </div>
              </div>
            )}

            {generationTime && (
              <div className="mb-4 p-4 bg-accent-light border border-accent rounded-lg accent-text">
                <div className="flex items-center gap-2">
                  <span>✨</span>
                  Generated in {generationTime.toFixed(2)} seconds
                </div>
              </div>
            )}


            <div className="border-t border-gray-200 pt-6">
              <p className="text-sm text-gray-500 mb-3">Try these example prompts:</p>
              <div className="flex flex-wrap gap-2">
                {[
                  "a misty forest panorama at sunrise",
                  "medieval castle on a hilltop",
                  "beach with a sunset"
                ].map((example, index) => (
                  <button
                    key={index}
                    className="px-4 py-2 text-sm bg-gray-100 hover:bg-accent-light hover:text-accent rounded-lg transition-colors border border-gray-200"
                    onClick={() => setPrompt(example)}
                    disabled={isLoading}
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>


        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold accent-text" style={{ fontFamily: 'Apercu, sans-serif' }}>Your 360° Panorama</h3>
                {imgSrc && (
                  <div className="text-sm text-gray-500">
                    Drag to explore • Scroll to zoom
                  </div>
                )}
              </div>
            </div>
            
            <div className="h-[70vh] bg-gray-50">
              {isLoading && !imgSrc ? (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-16 border-4 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-lg accent-text font-medium">Creating your panorama...</p>
                    <p className="text-sm text-gray-500 mt-2">This may take 45-60 seconds for high quality</p>
                  </div>
                </div>
              ) : imgSrc ? (
                <PanoramaViewer src={imgSrc} />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center text-gray-400">
                    <div className="text-8xl mb-6">🌍</div>
                    <p className="text-2xl font-light mb-2">Ready to teleport</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>


        <div className="text-center mt-16 text-gray-400 text-sm">
          <p>by shalini</p>
        </div>
      </div>
    </main>
  );
}
