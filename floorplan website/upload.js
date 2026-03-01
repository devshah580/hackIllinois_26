import { createClient } from '@supabase/supabase-js'
import fs from 'fs'
import path from 'path'
import dotenv from 'dotenv'

dotenv.config()

const SUPABASE_URL = "https://upsqvxtvlvxyuimngxil.supabase.co";
const SUPABASE_KEY = "sb_publishable_KSHPacBUw328_e-hVpgboA_OdLOcGhg";

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

const folder = '../data_without_tickers_png'
const files = fs.readdirSync(folder).filter(f => f.endsWith('.png'))

async function uploadFile(filePath, fileName) {
  const file = fs.readFileSync(filePath)
  const { data, error } = await supabase.storage
    .from('floorplans')
    .upload(fileName, file, {
      contentType: 'image/png',
      upsert: true
    })

  if (error) {
    console.error('Upload error for', fileName, error)
  } else {
    console.log('Uploaded:', fileName)
  }
}

async function uploadFolder() {
  for (const f of files) {
    const fullPath = path.join(folder, f)
    await uploadFile(fullPath, f)
    await new Promise(resolve => setTimeout(resolve, 200)) // 200ms delay
  }
}

uploadFolder()