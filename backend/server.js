const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

const app = express();
const server = http.createServer(app);
const io = require('socket.io')(server, { cors: { origin: '*' } });

// Optional MongoDB persistence
const { MongoClient } = require('mongodb');
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017';
const MONGO_DB = process.env.MONGO_DB || 'sms_spam_db';
let mongoClient = null;
let predsCollection = null;

async function initMongo(){
  try{
    mongoClient = new MongoClient(MONGO_URI);
    await mongoClient.connect();
    const db = mongoClient.db(MONGO_DB);
    predsCollection = db.collection('predictions');
    console.log('Connected to MongoDB for Express at', MONGO_URI, 'db', MONGO_DB);
  }catch(e){
    console.warn('Mongo init failed:', e.message);
    mongoClient = null; predsCollection = null;
  }
}
initMongo();

app.use(cors());
app.use(bodyParser.json());

// Serve frontend static files
app.use(express.static(path.join(__dirname, 'public')));

// Predict endpoint: calls the Python script
app.post('/predict', async (req, res) => {
  const { text, model } = req.body || {};
  if (!text) return res.status(400).json({ error: 'text is required' });

  try {
    const py = spawn('python3', [path.join(__dirname, 'predict.py'), '--text', text, '--model', model || 'default']);
    let out = '';
    let err = '';
    py.stdout.on('data', d => out += d.toString());
    py.stderr.on('data', d => err += d.toString());
    py.on('close', async code => {
      if (code !== 0) return res.status(500).json({ error: err || 'python exited with ' + code });
      try {
        const parsed = JSON.parse(out);
        // persist to MongoDB if available
        if (predsCollection){
          try{
            const doc = {
              text: parsed.input,
              transformed: parsed.transformed,
              steps: parsed.steps || null,
              prediction: parsed.prediction,
              probabilities: parsed.probabilities || null,
              model: model || 'default',
              ts: new Date()
            };
            await predsCollection.insertOne(doc);
          }catch(e){ console.warn('insert failed', e.message); }
        }
        res.json(parsed);
      } catch (e) {
        res.status(500).json({ error: 'failed to parse python output', raw: out, err });
      }
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// History endpoint: recent predictions from MongoDB
app.get('/history', async (req, res) => {
  if (!predsCollection) return res.status(503).json({ error: 'no database configured' });
  try{
    const rows = await predsCollection.find({}).sort({ ts: -1 }).limit(200).toArray();
    res.json({ items: rows });
  }catch(e){ res.status(500).json({ error: e.message }); }
});

// Simple endpoint to list available models (scans parent dir for model files)
app.get('/models', (req, res) => {
  const fs = require('fs');
  const root = path.resolve(__dirname, '..');
  try {
    const files = fs.readdirSync(root);
    const models = files.filter(f => f.endsWith('.pkl') || f.endsWith('.joblib'))
      .map(f => f.replace(/\.(pkl|joblib)$/, ''));
    res.json({ models: models.length ? models : ['model'] });
  } catch (e) {
    res.json({ models: ['model'] });
  }
});

// Metrics endpoint: serve metrics.json created by training script
app.get('/metrics', (req, res) => {
  const fs = require('fs');
  const metricsPath = path.resolve(__dirname, '..', 'metrics.json');
  if (!fs.existsSync(metricsPath)) return res.status(404).json({ error: 'metrics.json not found' });
  try {
    const raw = fs.readFileSync(metricsPath, 'utf8');
    const parsed = JSON.parse(raw);
    res.json(parsed);
  } catch (e) {
    res.status(500).json({ error: 'failed to read metrics.json', detail: e.message });
  }
});

// WebSocket for real-time detection
io.on('connection', socket => {
  console.log('ws connected', socket.id);
  socket.on('sms', async payload => {
    const text = payload && payload.text;
    if (!text) return socket.emit('error', { message: 'text required' });
    const py = spawn('python3', [path.join(__dirname, 'predict.py'), '--text', text, '--model', payload.model || 'default']);
    let out = '';
    let err = '';
    py.stdout.on('data', d => out += d.toString());
    py.stderr.on('data', d => err += d.toString());
    py.on('close', code => {
      if (code !== 0) return socket.emit('error', { message: err || 'python error' });
      try {
        const parsed = JSON.parse(out);
        socket.emit('prediction', parsed);
      } catch (e) {
        socket.emit('error', { message: 'parse error', raw: out });
      }
    });
  });
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => console.log(`Express server running on http://localhost:${PORT}`));
