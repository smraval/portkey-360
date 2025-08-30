"use client";

export default function Navbar() {
  const restartPanorama = () => {
    window.location.reload();
  };

  return (
    <nav className="fixed top-0 left-0 right-0 bg-[#f4f3ec]/95 backdrop-blur-sm border-b border-[#cbcdb6] z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold gradient-title" style={{ fontFamily: 'Apercu, sans-serif' }}>
              Portkey360
            </h1>
          </div>
          <button
            onClick={restartPanorama}
            className="px-6 py-2 rounded-full bg-[#a0b38c] hover:bg-[#8a9d7a] text-white font-medium transition-colors duration-200 hover:shadow-lg flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Restart
          </button>
        </div>
      </div>
    </nav>
  );
}
