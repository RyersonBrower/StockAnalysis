import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis, 
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

function App() {
  const [data, setData] = useState(null);
  const [ticker, setTicker] = useState("AAPL");
  const [debouncedTicker, setDebouncedTicker] =useState("AAPL");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Debounce user input (wait 1s after they stop typing)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedTicker(ticker);
    }, 1000);

    return () => clearTimeout(handler);
  }, [ticker]);

  // Fetch data whenever the debounced ticker changes
  useEffect(() => {
    if (!debouncedTicker) return;

    setLoading(true);
    setError(null);

    fetch(`${import.meta.env.VITE_API_URL}/api/data/${debouncedTicker}?limit=80`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch data");
        return res.json();
      })
      .then(setData)
      .catch((err) => {
        console.error(err);
        setError("No data available or API error");
        setData(null);
      })
      .finally(() => setLoading(false));
  }, [debouncedTicker]);

 return (
    <div className="app-container">
      <h1>📈 Stock Analysis Dashboard</h1>

      <div className="input-section">
        <label>Enter Ticker: </label>
        <input
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
        />
      </div>

      {loading && <p className="loading">Loading...</p>}
      {!ticker && <p className="error">{error}</p>}

      {data ? (
        <div className="data-section">
          {/* Fundamentals */}
          <div className="fundamentals-card">
            <h2>Fundamentals</h2>

            <div className="fundamentals-grid">
              {Object.entries(data.fundamentals).map(([key, value]) => (
                <div className="fundamentals-item" key={key}>
                  <span className="fundamentals-key">{key}</span>
                  <span className="fundamentals-value">{value}</span>
                </div>
                ))}
            </div>
          </div>


          {/* Price Chart */}
          <div className="chart-section">
            <h2>Price Trend (Close Price)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart 
                data={data.price_data.slice(-20)}
                margin={{top: 20, right: 30, left: 0, bottom: 5}}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" tick={false} />
                <YAxis domain={["auto", "auto"]}/>
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="close_price"
                  stroke="#007bff"
                  dot={false}
                  name="Close"
                />
                <Line
                  type="monotone"
                  dataKey="SM20"
                  stroke="#ff7300ff"
                  dot={false}
                  name="SMA20"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Price Data Table */}
          <div className="price-data">
            <h2>Price Data (last 20 rows)</h2>
            {data.price_data.length === 0 ? (
              <p>No price data available</p>
            ) : (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Open</th>
                      <th>High</th>
                      <th>Low</th>
                      <th>Close</th>
                      <th>Volume</th>
                      <th>SM20</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.price_data.slice(-20).map((row, idx) => (
                      <tr key={idx}>
                        <td>{row.timestamp}</td>
                        <td>{row.open_price}</td>
                        <td>{row.high_price}</td>
                        <td>{row.low_price}</td>
                        <td>{row.close_price}</td>
                        <td>{row.volume}</td>
                        <td>{row.SM20 ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      ) : (
        !loading && 
        !error && <p className="no-data">Enter a ticker to view stock data.</p>
      )}
    </div>
  );
}



  

export default App;




