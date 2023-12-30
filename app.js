const express=require("express"); 
const path = require('path');
global.app_root = path.resolve(__dirname);
const CFG     = require(app_root + '/config/config')
const { exec, execSync, spawn } = require("child_process")
const fs   = require('fs');

const app= express();        //binds the express module to 'app'

//setting the view engine as EJS. 
app.set('view engine', 'ejs');
//roots the views directory to public
app.set('views', 'public');
//tells express that the public folder is the static folder
app.use(express.static("public"));
//home route

// app.get("/", function(req,res){
//   res.send("Welcome to the world of science fiction, conflicting theories, fantasies and some eccentric nerds!")
// });

// nginx converts anvio.homd.org/anvio/ to anvio.homd.org/
app.get("/", function(req,res){
   
    console.log('In Anvio/:port')
    console.log('q',req.query)
    pg = req.query.pg
    if(!req.query.pg){
      pg = 'Veillonella_Atypica'
    }
    
  
    //let port = parseInt(req.query.port)
    let port = anvio_ports()
    if(!isInt(port)){
      return res.send("Bad port: '"+req.query.port+"'")
    }else if(port == 0){
       res.render('pages/index', {
        title: 'HOMD :: ANVIO',
        pg: pg,
        port:0,
        url:''
       })
       return
    }
    docker_params = ['exec','anvio','anvi-display-pan','-P',port,'-p',path.join(CFG.PATH_TO_PANGENOMES,pg+'/PAN.db'),'-g',path.join(CFG.PATH_TO_PANGENOMES,pg+'/GENOMES.db')]
    // docker exec -it anvio anvi-display-pan -P 8080 -p Veillonella_HMT780/PAN.db -g Veillonella_HMT780/GENOMES.db
    docker_params.push('--server-only')
    docker_params.push('--debug')
    console.log('docker '+docker_params.join(' '))
    var out = fs.openSync(path.join(CFG.PATH_TO_PANGENOMES,'anvio.'+port+'.log'), 'w');
    var proc = spawn(CFG.DOCKERPATH, docker_params, {
                    //env:{'PATH':CFG.PATH,'LD_LIBRARY_PATH':CFG.LD_LIBRARY_PATH},
                    detached: true, stdio: [ 'ignore', out, out ]  //, stdio: 'pipe'
                    //detached: false, stdio: 'pipe'  //, stdio: 'pipe'
     });
     proc.unref()  // this will allow proc to separate from node
     //console.log('proc',proc)
     //url = 'http://localhost:'+port
     //let url = 'http://localhost:3010/anvio?port='+port+'&pg='+pg
     let anviourl = CFG.URL_BASE+'/'+port +'/'
     console.log('URL',anviourl)
     res.render('pages/index', {
        title: 'HOMD :: ANVIO',
        pg: pg,
        port: port,
        url: anviourl
     })
         
     
     //return res.send('Good port: '+port.toString())
   
});
// app.get('/app', function (req, res) {
//   req.logout();
//   res.redirect('/app/login');
// });
// app.get('/target', function(req, res){  // must be the last get
//     console.log('In p8080')
//     
// })
function anvio_ports(){
    let open_ports, op
    // file to be present in docker 'anvio' container
    
    var open_ports_file = path.join(CFG.PATH_TO_PANGENOMES,'open_ports.txt')
    console.log('op file path',open_ports_file)
    try{
      op = fs.readFileSync(open_ports_file, 'utf8').toString()
      console.log('err1',op)
      //console.log('err1a',op.replaceAll('\'', '"'))
      //console.log('err1b',JSON.parse(op),typeof JSON.parse(op))
      //open_ports = JSON.parse(op.replaceAll('\'', '"'))
      open_ports = JSON.parse(op.replace(/\'/g, '"'));
      console.log('err2',open_ports)
      console.log('OK Using ports from open_ports_file')
    } catch (err) {
      console.log('Err: Using default open ports from config.js',err)
      open_ports = CFG.DEFAULT_OPEN_PORTS  // give it a try - it may work
    }
    
    if(open_ports.length > 0){
        op = open_ports[Math.floor(Math.random() * open_ports.length)]
        console.log('Returning Good Port',op)
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



app.listen(3010, function(){
        console.log("SERVER STARTED ON localhost:3010");     
})