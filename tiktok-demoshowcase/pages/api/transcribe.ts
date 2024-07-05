import { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from 'openai';
import fs from 'fs';
import path from 'path';

const apiKey = process.env.OPENAI_API_KEY;

if (!apiKey) {
  throw new Error('OPENAI_API_KEY environment variable is missing or empty');
}

const openai = new OpenAI({ apiKey });

const commands = [
  'A: like this video',
  'B: follow this creator',
  'C: scroll',
];


export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const filePath = path.join(process.cwd(), 'public', 'AUDIO.mp3'); // file to be transcribed
    const translation = await openai.audio.translations.create({
      file: fs.createReadStream(filePath),
      model: 'whisper-1',
    });

    console.log(translation.text);

    const prompt = `The user said: "${translation.text}". Determine which of the following commands best matches the text: ${commands.join(', ')}. Return only the uppercase letter associated with the command, and if no command matches, return '0'.`;

    const response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: 'You are an AI that identifies commands from a predefined list based on user input.' },
        { role: 'user', content: prompt },
      ],
    });

    const command = response.choices?.[0]?.message?.content?.trim();

    res.status(200).json({ command });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
}
