const express = require('express');
const fs = require('fs');
const app = express();
const bodyParser = require('body-parser');
const spawn = require("child_process").spawn;
const { linkType, get } = require("get-content");
const { json } = require('body-parser');

process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = 0

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header("Access-Control-Allow-Credentials", "true");
  res.header("Access-Control-Max-Age", "1800");
  res.header("Access-Control-Allow-Headers", "content-type");
  res.header("Access-Control-Allow-Methods","POST");
  next();
});
app.use(bodyParser.json());

app.post('/detectphishing', function(request, response) {
  console.log('POST /');
  console.dir(request.body);
      const url = request.body.url;
      console.log('==================')

      const startTime = Date.now();

      if(url.includes('chrome://')){
        dataResponse = {error:'ERROR_NEWTAB'}
        response.writeHead(200, {'Content-Type': 'application/json'});
        response.end(JSON.stringify(dataResponse));
      }
      else {

        const path = require('path');
      
        console.log("Starting Python process...");
        const mainPyPath = path.resolve(__dirname, '../main.py');
        const pythonProcess = spawn('python', [mainPyPath, url], { cwd: path.resolve(__dirname, '..') });

        pythonProcess.stdout.on('data', (data) => {
          response.writeHead(200, { 'Content-Type': 'application/json' });
          response.end(data.toString('utf8'));
        });

        pythonProcess.stderr.on('data', (errData) => {
          console.error('Python stderr:', errData.toString());
        });

        pythonProcess.on('close', (code) => {
          const endTime = Date.now();
          const totalTime = endTime - startTime;
          console.log(`[Timing] Response time: ${totalTime} ms`);
          console.log(`Python process exited with code ${code}`);
        });

      }
});

port = 3000;

// app.listen(port, '0.0.0.0', () => {
//   console.log(`Listening at http://0.0.0.0:${port}`);
// });

app.listen(port);
console.log(`Listening at http://localhost:${port}`);

