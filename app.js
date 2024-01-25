const express=require("express");
const router = express.Router(); 
const path = require('path');
global.app_root = path.resolve(__dirname);
const CFG     = require(app_root + '/config/config')
const { exec, execSync, spawn } = require("child_process")
const fs   = require('fs');
var bodyParser = require('body-parser')
const app= express();        //binds the express module to 'app'
// create application/json parser
app.use(bodyParser.urlencoded({
    extended: false,         // allows for richer json like experience https://www.npmjs.com/package/qs#readme
    limit: '50mb',          // size of body
    parameterLimit: 100000 // number of parameters
}));
app.use(bodyParser.json());
 
// create application/x-www-form-urlencoded parser
var urlencodedParser = bodyParser.urlencoded({ extended: false })
//setting the view engine as EJS. 

//roots the views directory to public
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
//tells express that the public folder is the static folder
app.use(express.static("public"));

//const DEFAULT_OPEN_PORTS = [8080,8081,8082,8083,8084,8085,8086,8087,8088,8089]
const DEFAULT_OPEN_PORTS = [8080,8081,8082,8083,8084,8085,8086]
//const DEFAULT_OPEN_PORTS = [8080, 8081]
//home route

app.get("/anvio_test", function(req,res){
    res.send("Welcome to anvio_test")
});
// app.get("/anvio", function(req,res){
//     res.send("Welcome to the world of science fiction, conflicting theories, fantasies and some eccentric nerds!")
// });
// nginx converts anvio.homd.org/anvio/ to anvio.homd.org/
app.get("/", function(req,res){
   
    console.log('In Anvio/:port',req.query)
    pg = req.query.pg
    if(!req.query.pg){
      return res.send("No Pangenome")
    }
    
  
    //let port = parseInt(req.query.port)
    let port = anvio_ports()
    if(!isInt(port)){
      return res.send("Bad port: '"+req.query.port+"'")
    }else if(port == 0){
       res.render('pages/index', {
        title: 'HOMD :: ANVIO',
        pg: pg,
        port: 0,
        url:''
       })
       return
    }
    docker_params = ['exec','-i','anvio','anvi-display-pan','-p',path.join(CFG.PATH_TO_PANGENOMES,pg+'/PAN.db'),'-g',path.join(CFG.PATH_TO_PANGENOMES,pg+'/GENOMES.db')]
    // docker exec -it anvio anvi-display-pan -P 8080 -p Veillonella_HMT780/PAN.db -g Veillonella_HMT780/GENOMES.db
    docker_params.push('-P',port)
    docker_params.push('--server-only')  // means that browser is NOT called
    docker_params.push('--debug')         // means that output is recorded as log entries: stdout or file
    docker_params.push('--read-only')    // means default state will not be overwritten
    
    console.log(CFG.DOCKERPATH+' '+docker_params.join(' '))
    var out = fs.openSync(path.join(CFG.PATH_TO_PANGENOMES, port+'.pg.log'), 'w');
    var proc = spawn(CFG.DOCKERPATH, docker_params, {
                    //env:{'PATH':CFG.PATH,'LD_LIBRARY_PATH':CFG.LD_LIBRARY_PATH},
                    detached: true, stdio: [ 'ignore', out, out ]  //, stdio: 'pipe'
                    //detached: false, stdio: 'pipe'  //, stdio: 'pipe'
     });
     proc.unref()  // this will allow proc to separate from node
     //console.log('proc',proc)
     //url = 'http://localhost:'+port
     //let url = 'http://localhost:3010/anvio?port='+port+'&pg='+pg
     let anviourl
     if(CFG.DBHOST == 'localhost'){
         anviourl = CFG.URL_BASE+':'+port +'/'
     }else{
         // app/index.html?rand=af545a01
         anviourl = CFG.URL_BASE+'/'+port + '/app/index.html?rand=' + makeid(8)
     }
     console.log('URL',anviourl)
     res.render('pages/index', {
        title: 'HOMD :: ANVIO',
        pg: pg,
        port: port,
        url: anviourl
     })
         
     
     //return res.send('Good port: '+port.toString())
   
});

app.post("/wait_on_anvio", async(req,res)=>{
    console.log('in wait => req.body',req.body)
    up_file = path.join(CFG.PATH_TO_PANGENOMES,req.body.port+'.up')
    // continue to look for file up to 2 min
    const isFile = await holdBeforeFileExists(up_file, CFG.WAIT_TIME);
    //console.log('file',isFile,up_file)
    if(isFile){
        console.log('returning isFile true: ','"'+req.body.port+'.up"')
        return res.send('isFile')  // 
        
    } else {
        console.log('returning false ',req.body.port)
        return res.send('Failed to start anvio pangenome. <small>(Or too long to create an UpFile)</small>');
    }

});
// app.get('/app', function (req, res) {
//   req.logout();
//   res.redirect('/app/login');
// });
// app.get('/target', function(req, res){  // must be the last get
//     console.log('In p8080')
//     
// })
function makeid(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
      counter += 1;
    }
    return result;
}
function anvio_ports(){
    let open_ports, op
    // file to be present in docker 'anvio' container
    
    var open_ports_file = path.join(CFG.PATH_TO_PANGENOMES,'open_ports.txt')
    console.log('op file path',open_ports_file)
    try{
      op = fs.readFileSync(open_ports_file, 'utf8').toString()
      open_ports = JSON.parse(op.replace(/\'/g, '"'));
      if(! open_ports || open_ports.length === 0){
         return 0
      }
      console.log('open_ports',open_ports)
      
    } catch (err) {
      console.log('Err: Using default open ports from config.js',err)
      open_ports = DEFAULT_OPEN_PORTS  // give it a try - it may work
    }
    
    if(open_ports.length > 0){
        op = open_ports[Math.floor(Math.random() * open_ports.length)]
        console.log('Good Port',op)
        return op;
    }else{
        return 0
    }
    
}
function isInt(value) {
  return !isNaN(value) && 
         parseInt(Number(value)) == value && 
         !isNaN(parseInt(value, 10));
} 
/**
*
* @param {String} filePath
* @param {Number} timeout
* @returns {Promise<Boolean>}
https://stackoverflow.com/questions/26165725/nodejs-check-file-exists-if-not-wait-till-it-exist
*/
const holdBeforeFileExists = async (filePath, timeout) => {
  console.log('holdBeforeFileExists begin')
  timeout = timeout < 1000 ? 1000 : timeout
  try {
    var nom = 0
      return new Promise(resolve => {
        var inter = setInterval(() => {
          nom = nom + 100
          if (nom >= timeout) {
            clearInterval(inter)
            //maybe exists, but my time is up! 
            resolve(false)
          }

          if (fs.existsSync(filePath) && fs.lstatSync(filePath).isFile()) {
            clearInterval(inter)
            //clear timer, even though there's still plenty of time left
            resolve(true)
          }
        }, 100)
      })
  } catch (error) {
    console.log('holdBeforeFileExists err')
    return false
  }
}


app.listen(3010, function(){
        console.log("SERVER STARTED ON localhost:3010");     
})