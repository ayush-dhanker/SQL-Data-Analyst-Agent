import ChatBox from "./components/ChatBox";
import "./App.css";

export default function App() {
  return (
    <div className="app">
      <header className="header">
        <h1>SQL Analyst Agent</h1>
        <p>Powered by LangGraph + Groq + PostgreSQL</p>
      </header>
      <main>
        <ChatBox />
      </main>
    </div>
  );
}