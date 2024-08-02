const API_BASE_URL = 'http://localhost:5000/api';

export async function getChanges(params: {
  page?: number;
  limit?: number;
  company?: string;
  changeSize?: string;
  fromDate?: string;
  toDate?: string;
}) {
  const queryParams = new URLSearchParams(
    Object.entries(params).filter(([_, v]) => v != null) as [string, string][]
  );
  const response = await fetch(`${API_BASE_URL}/changes?${queryParams}`);
  if (!response.ok) {
    throw new Error('Failed to fetch changes');
  }
  return response.json();
}

export async function getChangeDetails(id: string) {
  const response = await fetch(`${API_BASE_URL}/changes/${id}`);
  if (!response.ok) {
    throw new Error('Failed to fetch change details');
  }
  return response.json();
}

export async function getCompanies() {
  const response = await fetch(`${API_BASE_URL}/companies`);
  if (!response.ok) {
    throw new Error('Failed to fetch companies');
  }
  return response.json();
}