void OnInit()
{
EventSetTimer(10);
if (trade_decider()==false || trade_decider()==true)
{
if (enter_trade()==true)
{conn_to_sock();}
}
//reason();
OnDeinit();
}
void reason()
{
//char indicators[4];
//indicators[0:3]=1;
}



void OnDeinit()
{
}

string trade_decider()  //decides if i can enter trade
{

if(nv()=="true" && qqe()=="long" && basel()=="long")
{
Print(basel(),"\n",qqe(),"\n",nv());
MessageBox("basic entry:long");
return true;}
else if(nv()=="true" && qqe()=="c-long" && basel()=="long")
{
Print(basel(),"\n",qqe(),"\n",nv());
MessageBox("continuation:long");
return true;}
else if(nv()=="true" & qqe()=="short" & basel()=="short")
{Print(basel(),"\n",qqe(),"\n",nv());
MessageBox("basic entry:short");
return false;}
else if(nv()=="true" & qqe()=="c-short" & basel()=="short")
{
Print(basel(),"\n",qqe(),"\n","\n",nv());
MessageBox("continuation:short");
return false;}
else{
Print(basel(),"\n",qqe(),"\n",nv());
Print("no new signal");
return "none";}
}
//baseline function checks if baseline is long or short
string basel()
{

//define variables
double basel_array[];
MqlRates b_rate[];

//create indicator handle
int basel_handle=iCustom(Symbol(),PERIOD_CURRENT,"Downloads\AllAverages_v4.9_MT5");
//retrieve info from buffer handle
int _1=CopyBuffer(basel_handle,0,0,2,basel_array);
int _2=CopyRates(Symbol(),PERIOD_CURRENT,1,1,b_rate);


//decide if long or short

if(SymbolInfoDouble(Symbol(),SYMBOL_BID)>basel_array[1] && 
b_rate[0].close<basel_array[0])
{return "long";
}
else if(SymbolInfoDouble(Symbol(),SYMBOL_BID)<basel_array[1] &&
b_rate[0].close>basel_array[0])
{return "short";}

else{return "none";}
}

//qqe function,checks if indicator is long or short
string qqe()
{
//---defining variables
double today[2]={};
double yesterday[2];
double   qqe_array[];
int x;
//reading indicator value
int qqe_handle=iCustom(Symbol(),PERIOD_CURRENT,"Downloads\qqe");
for(x=0;x<=1;x=x+1)
{
int   qqe=CopyBuffer(qqe_handle,x,0,2,qqe_array);
int   m=GetLastError(); 
today[x]=qqe_array[1];
yesterday[x]=qqe_array[0];
};

//Printing results
if(today[0]>today[1] && yesterday[0]<yesterday[1])
{
return "long";
}
else if(today[0]<today[1] && yesterday[0]>yesterday[1])
{
return "short";
}
else if(today[0]>today[1])
{
return "c-long";
}
else if(today[0]<today[1])
{
return "c-short";
}
return "none";

}
  
//nv function,checks if indicator is long or short
string nv()
{
//defining variables
double nv_array[];
double MA_array[];
int x;
double nvres[2];
//Reading indicator values
int nv_handle=iCustom(Symbol(),PERIOD_CURRENT,"Downloads\\normalizedvolume",0,0,7,15);
int _=CopyBuffer(nv_handle,0,0,1,nv_array);


//Printing results
if(nv_array[0]>1)
{
return "true";
}
else{return "false";}
}


bool enter_trade()  //enters the trade
{
volume_calc();
return true;
}
bool OnTimer()
{

bool start=true;
//checks whether the time is right and if any trades are placed in order to enter a trade

if(timestart()==true || timestart()==false)
{bool end=timeend();
//iterates until time is up
while(timeend()==false)
{
if (PositionSelect(Symbol())==false)
{
volume_calc();
return true;
}
else{return false;}
}
return false;
}
else{Print("not the time");
return false;}
}

void volume_calc()
{
double volume;
double ATR_array[];
int ATR_handle=iATR(Symbol(),PERIOD_CURRENT,14);
int _=CopyBuffer(ATR_handle,0,0,1,ATR_array);
double stoploss=ATR_array[0]*10000*1.5;
double   balance=AccountInfoDouble(ACCOUNT_BALANCE);
string   _1="USD";
string   _2=StringSubstr(Symbol(),3,-1);
string _3=StringSubstr(Symbol(),3,-1);
bool _4=StringAdd(_2,"USD");
bool _5=StringAdd(_1,_3);
string _6=StringSubstr(Symbol(),3,-1); 
double risk=balance*0.02;
//if pair has a USD as quote pair
if(_6=="USD")
{
double volume=NormalizeDouble(risk/stoploss/2/10,2);
double rate=SymbolInfoDouble(Symbol(),SYMBOL_BID);
Print(volume);
enter(volume);
}
//if quote pair is not USD
else
{
if(SymbolSelect(_1,true)==true)
{double rate=SymbolInfoDouble(_1,SYMBOL_BID);
double volume=NormalizeDouble(((risk*rate)/stoploss/2/10),2);
Print(volume);
enter(volume);
}
else if (SymbolSelect(_2,true)==true)
{double  rate=SymbolInfoDouble(_2,SYMBOL_BID);
double  volume=NormalizeDouble(((risk/rate)/stoploss/2/10),2);
Print(volume);
enter(volume);
}
}
Print(volume);
return;
}
//function to enter a trade
bool enter(double volume)
{
MqlTradeRequest request={};
MqlTradeResult result={};
request.action=TRADE_ACTION_DEAL;
request.symbol=Symbol();
request.volume=volume;
if(trade_decider()==true)
{request.type=ORDER_TYPE_BUY;}
else if(trade_decider()==false)
{request.type=ORDER_TYPE_SELL;}
bool  o=OrderSend(request,result);
bool m=OrderSend(request,result);

Print(result.retcode);
Print("entered");

return true;
}


//function which checks the time in order to enter or exit a trade
bool timestart()
{
MqlDateTime time;
bool _=TimeToStruct(TimeLocal(),time);
MqlDateTime start;
start.hour=23;
start.min=59;
if(start.hour==time.hour && start.min==time.min)
{return true;}
else{return false;}
}

bool timeend()
{
MqlDateTime time;
bool _=TimeToStruct(TimeLocal(),time);
MqlDateTime end;
end.hour=0;
end.min=0;
if(end.hour==time.hour && end.min==time.min)
{return true;}
else{return false;}

}


void conn_to_sock()   //connects to server socket to send informationfrom mt5 terminal
{clientsock();}



int clientsock()
  {
int mq5sock;
const string address="10.246.60.70";
uint port=2023;
uint  timeo=20000;
uchar  mq5buffer[]={};
uchar symbolname[]; 
uchar position[]; 
  
 
int ATRhandle=iCustom(_Symbol,PERIOD_CURRENT,
"Examples\ATR");
double ATR=Indivalue(ATRhandle);
uint  bufflength=StringToCharArray(ATR,mq5buffer,0,WHOLE_ARRAY);
uint  sym_len=StringToCharArray(Symbol(),symbolname,0,WHOLE_ARRAY);
uint pos_len=StringToCharArray(trade_decider(),position,0,WHOLE_ARRAY);
mq5sock = SocketCreate(SOCKET_DEFAULT);
bool  con = SocketConnect(mq5sock,address,port,timeo);
bool  sockcon=  SocketIsConnected(mq5sock);
Print(sockcon);

int   socksend=SocketSend(mq5sock,mq5buffer,bufflength);

int socksend2=SocketSend(mq5sock,symbolname,sym_len);

int socksend3=SocketSend(mq5sock,position,pos_len);


 return INIT_SUCCEEDED;
 }
\
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(int mq5sock)
  {
bool close=SocketClose(mq5sock);
  }

double Indivalue(int ATRhandle)
  {
//---
double ATRarray[];
double value=CopyBuffer(ATRhandle,0,0,1,ATRarray);
return ATRarray[0];
  }




