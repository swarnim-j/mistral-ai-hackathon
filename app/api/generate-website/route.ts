import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import * as process from 'process';

export async function POST(request: Request) {
  const { prompt } = await request.json();

  return new Promise((resolve) => {
    const env = { ...process.env };
    
    if (!env.MISTRAL_API_KEY) {
      console.error('MISTRAL_API_KEY is not set in the environment');
      resolve(NextResponse.json({ error: 'MISTRAL_API_KEY is not set' }, { status: 500 }));
      return;
    }

    const pythonProcess = spawn('python', ['test_utils.py', prompt], { env });

    let outputData = '';
    let errorData = '';

    pythonProcess.stdout.on('data', (data) => {
      outputData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
    });

    pythonProcess.on('close', (code) => {
      console.log('Python process exited with code:', code);
      console.log('Output data:', outputData);
      console.log('Error data:', errorData);

      if (code !== 0 || errorData) {
        console.error('Error:', errorData);
        resolve(NextResponse.json({ error: 'An error occurred while generating the website', details: errorData }, { status: 500 }));
      } else {
        try {
          const websiteData = JSON.parse(outputData);
          resolve(NextResponse.json(websiteData));
        } catch (error) {
          console.error('Error parsing Python script output:', error);
          console.error('Raw output:', outputData);
          resolve(NextResponse.json({ error: 'An error occurred while processing the generated website', details: outputData }, { status: 500 }));
        }
      }
    });
  });
}