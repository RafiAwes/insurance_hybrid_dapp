import { useState } from 'react'
import WalletConnect from './components/WalletConnect'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <header className="App-header">
        <h1>Health Insurance DApp</h1>
        <WalletConnect />
        <p>Welcome to the decentralized health insurance platform.</p>
        <div className="card">
          <button onClick={() => setCount((count) => count + 1)}>
            count is {count}
          </button>
        </div>
      </header>
    </div>
  )
}

export default App