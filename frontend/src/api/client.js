const API_BASE = "/api";

export async function sendChatMessage(query, authorityFilter = "") {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: query,
      authority_filter: authorityFilter,
      use_cache: true,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Chat API error ${response.status}: ${errorText}`);
  }

  return await response.json();
}

export async function fetchHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error(`Health API error ${response.status}`);
  }
  return await response.json();
}

export async function fetchDocumentList() {
  const response = await fetch(`${API_BASE}/documents`);
  if (!response.ok) {
    throw new Error(`Documents API error ${response.status}`);
  }
  return await response.json();
}

export async function fetchCacheStats() {
  const response = await fetch(`${API_BASE}/cache/stats`);
  if (!response.ok) {
    throw new Error(`Cache stats API error ${response.status}`);
  }
  return await response.json();
}

export async function clearSystemCache() {
  const response = await fetch(`${API_BASE}/cache/clear`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`Clear cache API error ${response.status}`);
  }
  return await response.json();
}

export async function triggerReSeed() {
  const response = await fetch(`${API_BASE}/seed`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error(`Re-seed API error ${response.status}`);
  }
  return await response.json();
}

export async function uploadDocumentFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Upload API error ${response.status}: ${errorText}`);
  }

  return await response.json();
}