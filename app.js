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
    docker_preparams = ['exec','-id','anvio']
//     docker exec -h Options:
//   -d, --detach               Detached mode: run command in the background
//       --detach-keys string   Override the key sequence for detaching a container
//   -e, --env list             Set environment variables
//       --env-file list        Read in a file of environment variables
//   -i, --interactive          Keep STDIN open even if not attached
//       --privileged           Give extended privileges to the command
//   -t, --tty                  Allocate a pseudo-TTY
//   -u, --user string          Username or UID (format: "<name|uid>[:<group|gid>]")
//   -w, --workdir string       Working directory inside the container
    pan_params = [CFG.ANVIPATH+'anvi-display-pan','-p',path.join(CFG.PATH_TO_PANGENOMES,pg+'/PAN.db'),'-g',path.join(CFG.PATH_TO_PANGENOMES,pg+'/GENOMES.db')]
    // docker exec -it anvio anvi-display-pan -P 8080 -p Veillonella_HMT780/PAN.db -g Veillonella_HMT780/GENOMES.db
    pan_params.push('-P',port)
    pan_params.push('--server-only')  // means that browser is NOT called
    pan_params.push('--debug')         // means that output is recorded as log entries: stdout or file
    pan_params.push('--read-only')    // means default state will not be overwritten
    // create bash script and run that
    var use_bash_script_envelope = true
    
    var logfn = path.join(CFG.PATH_TO_PANGENOMES, port+'.pg.log')
    var logout = fs.openSync(logfn, 'w');
    console.log(pan_params.join(' '))
    
    if( use_bash_script_envelope ){
      var bash_script_file = path.join(CFG.PATH_TO_PANGENOMES, port+'.sh')
      var txt = '#!/usr/bin/sh\n\n'
      //var cmd = txt + CFG.DOCKERPATH + ' '+(docker_preparams.concat(pan_params)).join(' ') +' &>'+logfn+'\n'
      var cmd = txt +' '+pan_params.join(' ') +' &>'+logfn+'\n'
    
      fs.writeFile(bash_script_file, cmd, function (err) {
        if (err){
          console.log(err)
        }
        fs.chmod(bash_script_file, 0o755, err => {
        if (err) {
          console.log(err)
        }else{
           console.log('mode changed',bash_script_file)
           // console.log('LOG', path.join(CFG.PATH_TO_PANGENOMES, port+'.pg.log'))
           //console.log('running',CFG.DOCKERPATH+' '+docker_preparams.concat(['sh ',bash_script_file]).join(' '))
           console.log('Running: '+bash_script_file)
           
           //const proc = exec(bash_script_file);
           //var spawncmd = CFG.DOCKERPATH +' '+docker_preparams.concat(['/bin/sh', '-c', bash_script_file]).join(' ')
           var spawncmd = ['/bin/sh', '-c', bash_script_file]
           console.log('spawncmd',spawncmd.join(' '))
           //const proc = spawn(CFG.DOCKERPATH, docker_preparams.concat(['/bin/sh', '-c', bash_script_file]), {
           const proc = spawn(['/bin/sh', '-c', bash_script_file].join(' '), {
                    //env:{'PATH':CFG.PATH,'LD_LIBRARY_PATH':CFG.LD_LIBRARY_PATH},
                    env:{'PATH':CFG.PATH},
                    stdio: ['ignore'], detached: true  //, stdio: 'pipe'
                    //detached: false, stdio: 'pipe'  //, stdio: 'pipe'
            });
            proc.unref()  // this will allow proc to separate from node
          }
        });

      });
      
    }else{  // NO bash script
    
        console.log('LOG', path.join(CFG.PATH_TO_PANGENOMES, port+'.pg.log'))
        console.log('Using Instead',pan_params.join(' '))
        var proc = spawn(pan_params.join(' '), {
                    //env:{'PATH':CFG.PATH,'LD_LIBRARY_PATH':CFG.LD_LIBRARY_PATH},
                    env:{'PATH':CFG.PATH},
                    detached: true, stdio: [ 'ignore', logout, logout ]  //, stdio: 'pipe'
                    //detached: false, stdio: 'pipe'  //, stdio: 'pipe'
        });
        proc.unref()  // this will allow proc to separate from node
     //console.log('proc',proc)
     //url = 'http://localhost:'+port
     //let url = 'http://localhost:3010/anvio?port='+port+'&pg='+pg
    }  // bash yes/no
    
     let anviourl
     if(CFG.DBHOST == 'localhost'){
         anviourl = CFG.URL_BASE+':'+port +'/'
     }else{
         // app/index.html?rand=af545a01
         anviourl = CFG.URL_BASE+'/'+port + '/app/index.html?rand=' + makerando(8)
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
    console.log('in wait ('+CFG.WAIT_TIME+' msec)=> req.body',req.body)
    up_file = path.join(CFG.PATH_TO_PANGENOMES,req.body.port+'.up')
    console.log('in wait looking for',up_file)
    // continue to look for file up to 2 min
    const isFile = await holdBeforeFileExists(up_file, CFG.WAIT_TIME);
    console.log('file',isFile,up_file)
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
function makerando(length) {
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
  console.log('timeout',timeout)
  try {
    var nom = 0
      return new Promise(resolve => {
        var inter = setInterval(() => {
          nom = nom + 100
          //console.log('nom',nom,'timeout',timeout)
          if (nom >= timeout) {
            clearInterval(inter)
            //maybe exists, but my time is up! 
            
            resolve(false)
          }
          
          if (fs.existsSync(filePath) && fs.lstatSync(filePath).isFile()) {
            clearInterval(inter)
            console.log("clear timer, even though there's still plenty of time left")
            resolve(true)
          }
        }, 1000)
      })
  } catch (error) {
    console.log('holdBeforeFileExists err')
    return false
  }
}


app.listen(3010, function(){
        console.log("SERVER STARTED ON localhost:3010");     
})