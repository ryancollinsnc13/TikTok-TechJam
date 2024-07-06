import { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from 'openai';
import fs from 'fs';
import path from 'path';
import formidable, { Fields, Files } from 'formidable';

const apiKey = process.env.OPENAI_API_KEY;

if (!apiKey) {
  throw new Error('OPENAI_API_KEY environment variable is missing or empty');
}

const openai = new OpenAI({ apiKey });

const commands = [
  '1: Go to For You Page',
  '2: Upload a video',
  '3: Go to my profile page',
  '4: Log out',
  '5: Like this video',
  '6: Leave a comment', // figure out how to choose comment, and confirm with user
  '7: Search for text', // also return search content
  '8: Go to video owner profile',
  '9: Scroll to next video',
  '10: Edit profile',
  '11: Change name',
  '12: Change bio',
];

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const form = new formidable.IncomingForm();

  form.parse(req, async (err: any, fields: Fields, files: Files) => {
    if (err) {
      return res.status(500).json({ error: 'Error parsing the files' });
    }

    // Ensure files.audio is properly handled
    const audioFile = Array.isArray(files.audio) ? files.audio[0] : files.audio;
    if (!audioFile) {
      return res.status(400).json({ error: 'No audio file provided' });
    }

    const tempDir = path.join(process.cwd(), 'public');
    const filePath = path.join(tempDir, audioFile.newFilename);

    // Ensure the file is saved correctly
    fs.renameSync(audioFile.filepath, filePath);

    try {
      const translation = await openai.audio.translations.create({
        file: fs.createReadStream(filePath),
        model: 'whisper-1',
      });

      console.log(translation.text);

      const prompt = `The user said: "${translation.text}". Determine which of the following commands best matches the text: ${commands.join(', ')}. Return only the number associated with the command, and if no command matches, return '0'.`;

      const response = await openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: 'You are an AI that identifies commands from a predefined list based on user input.' },
          { role: 'user', content: prompt },
        ],
      });

      const command = response.choices?.[0]?.message?.content?.trim();
      

      fs.unlinkSync(filePath);

      res.status(200).json({ command });
    } catch (error: any) {
   
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
      res.status(500).json({ error: error.message });
    }
  });
}
