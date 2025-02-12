import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [data, setData] = useState([])
  const apiBaseUrl = '/api';  // Change if your Flask app runs on a different host/port

  // Add a new CCTV feed
  async function addCCTV() {
    debugger
    const feedUrl = document.getElementById('feedUrl').value;
    if (!feedUrl) {
      alert('Please enter a feed URL.');
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/add-camera`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: feedUrl })
      });

      const result = await response.json();
      alert(result.message || 'CCTV added successfully.');
    } catch (error) {
      console.error('Error adding CCTV:', error);
    }
  }

  // Remove a CCTV feed
  async function removeCCTV() {
    const removeUrl = document.getElementById('removeUrl').value;
    if (!removeUrl) {
      alert('Please enter a feed URL to remove.');
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/remove-camera`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: removeUrl })
      });

      const result = await response.json();
      alert(result.message || 'CCTV removed successfully.');
    } catch (error) {
      console.error('Error removing CCTV:', error);
    }
  }

  // Fetch real-time people count data
  async function fetchData() {
    debugger
    try {
      const response = await fetch(`${apiBaseUrl}/get-all`);
      const data = await response.json();
      setData(data)
      // const dataDisplay = document.getElementById('dataDisplay');
      // dataDisplay.innerHTML = '';

      // if (Object.keys(data).length === 0) {
      //   dataDisplay.innerHTML = '<p>No data available.</p>';
      //   return;
      // }

      // for (const [url, info] of Object.entries(data)) {
      //   const item = document.createElement('div');
      //   item.classNameName = 'data-item';
      //   item.innerHTML = `
      //       <strong>URL:</strong> ${url}<br>
      //       <strong>People Count:</strong> ${info.count}<br>
      //       <strong>Last Updated:</strong> ${info.timestamp}
      //     `;
      //   dataDisplay.appendChild(item);
      // }
    } catch (error) {
      setData({})
    }
  }
  useEffect(() => {

    const interval = setInterval(() => {
      fetchData()
    }, 1000)
  }, [])
  return (
    <>
      <h1>CCTV People Count Dashboard</h1>

      <div className="form-container">
        <h2>Add New CCTV Feed</h2>
        <input type="text" id="feedUrl" placeholder="Enter CCTV Feed URL" />
        <button onClick={addCCTV}>Add CCTV</button>
      </div>

      <div className="form-container">
        <h2>Remove CCTV Feed</h2>
        <input type="text" id="removeUrl" placeholder="Enter CCTV Feed URL to Remove" />
        <button onClick={removeCCTV}>Remove CCTV</button>
      </div>

      <div className="data-container">
        <h2>Real-Time People Count Data</h2>
        <button onClick={fetchData}>Refresh Data</button>
        <div id="dataDisplay"></div>
      </div>
      <table width={"100%"} border={1}>
        <tr>
          <th>URL:</th>
          <th>People Count:</th>
          <th>Last Updated:</th>
        </tr>
        {
          Object.entries(data).map((d) => {
            console.log(d)
            const [url, info] = d
            return <>
              <tr>
                <td> {url} </td>
                <td> {info.count} </td>
                <td> {info.timestamp} </td>
              </tr>

            </>

          })
        }
      </table>
    </>
  )
}

export default App
