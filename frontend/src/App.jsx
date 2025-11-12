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
  const [loading, setLoading] = useState(false);

  const fetchData = () => {
    if (!ticker) return;
    setLoading(true);
    fetch(`${import.meta.env.VITE_API_URL}/api/data/${ticker}?limit=80`)
      .then((res) => res.json())
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
      fetchData();
    }, [ticker, fetchData]);


  useEffect(() => {
    const interval = setInterval(fetchData, 300000);
    return () => clearInterval(interval);
  }, [ticker]);

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

      {loading && <p>Loading...</p>}
      {!ticker && <p>Please enter a ticker.</p>}

      {data ? (
        <div className="data-section">
          {/* Fundamentals */}
          <div className="fundamentals">
            <h2>Fundamentals</h2>
            <table>
              <tbody>
                {Object.entries(data.fundamentals).map(([key, value]) => (
                  <tr key={key}>
                    <td className="key">{key}</td>
                    <td className="value">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Price Chart */}
          <div className="chart-section">
            <h2>Price Trend (Close Price)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.price_data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" hide={false} />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="close_price"
                  stroke="#007bff"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="SM20"
                  stroke="#ff7300"
                  dot={false}
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
        !loading && ticker && <p>No data available.</p>
      )}
    </div>
  );
}



  

export default App;




