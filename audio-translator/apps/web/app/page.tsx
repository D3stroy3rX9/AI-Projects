export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white p-8">
      <div className="max-w-6xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🎤 Audio Auto-Translator
          </h1>
          <p className="text-gray-600">
            Real-time voice translation supporting 100+ languages
          </p>
        </header>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <p className="text-center text-gray-500">
            Frontend ready! Next step: Add audio recording component.
          </p>
        </div>
      </div>
    </main>
  )
}
