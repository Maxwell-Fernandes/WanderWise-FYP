import { NavLink, Route, Routes } from 'react-router-dom'
import Module1SimulationPage from './pages/Module1SimulationPage'
import Module2SimulationPage from './pages/Module2SimulationPage'
import Module4SimulationPage from './pages/Module4SimulationPage'

export default function App() {
  return (
    <div className="container">
      <h1>WanderWise Notebook Simulator</h1>
      <nav className="card">
        <NavLink to="/">Module 1</NavLink>
        <NavLink to="/module2">Module 2</NavLink>
        <NavLink to="/module4">Module 4</NavLink>
      </nav>
      <Routes>
        <Route path="/" element={<Module1SimulationPage />} />
        <Route path="/module2" element={<Module2SimulationPage />} />
        <Route path="/module4" element={<Module4SimulationPage />} />
      </Routes>
    </div>
  )
}
