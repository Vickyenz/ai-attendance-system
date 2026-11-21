import { Route, Routes } from 'react-router-dom'
import { PalettePage } from './pages/PalettePage'

export function App() {
  return (
    <Routes>
      <Route path="/" element={<PalettePage />} />
      <Route path="*" element={<PalettePage />} />
    </Routes>
  )
}
