import axios from 'axios';

const client = axios.create({
  baseURL: 'http://localhost:8000',
});

export async function getContributorActivity(granularity = 'weekly') {
  const response = await client.get('/metrics/contributor-activity', {
    params: { granularity },
  });
  return response.data;
}

export async function getDeployFrequency(granularity = 'weekly') {
  const response = await client.get('/metrics/deploy-frequency', {
    params: { granularity },
  });
  return response.data;
}

export async function getLeadTime(granularity = 'weekly') {
  const response = await client.get('/metrics/lead-time', {
    params: { granularity },
  });
  return response.data;
}