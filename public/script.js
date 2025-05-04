document.getElementById('recipe-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const url = document.getElementById('url').value;
    const allergensDiv = document.getElementById('allergens');
    allergensDiv.textContent = "Processing...";
    try {
      const response = await fetch('http://localhost:8000/extract-allergens', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const data = await response.json();
      if (data.status === "success" && data.result && data.result.allergens) {
        if (data.result.allergens.length === 0) {
          allergensDiv.innerHTML = "<span style='color:#2e7d32;'>No allergens detected 🎉</span>";
        } else {
          allergensDiv.innerHTML = "Allergens: <br><span style='font-size:1.5em;'>" +
            data.result.allergens.map(a => `<span style="margin-right:1em;">${a}</span>`).join('') +
            "</span>";
        }
      } else {
        allergensDiv.textContent = "No allergens found or error in response.";
      }
    } catch (err) {
      allergensDiv.textContent = "Error: " + err;
    }
  });
  