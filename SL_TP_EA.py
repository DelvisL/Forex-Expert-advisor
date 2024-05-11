import socket
import MetaTrader5 as mt5
import re,time,pdb,time,threading,sys,os,traceback,subprocess,os,tabulate
import win32service,servicemanager,win32serviceutil,win32evtlog

#Class for controlling the windows service
class TradingService(win32serviceutil.ServiceFramework):
    _svc_name_="SL_TP_EAupdated"
    _svc_display_name_="ForexTradingService2"
    _exe_name_ = "ForextradingService2"
    _svc_description_ = ("This service controls trading for limits for MetaTrader accounts")


    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)



    def SvcStop(self):
        try:
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)
            self.is_alive=False
        except:
            servicemanager.LogErrorMsg(traceback.format_exc())


    def SvcDoRun(self):
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.is_alive=True
            self.main()
        except:
            servicemanager.LogErrorMsg(traceback.format_exc())


    def main(self):
        while self.is_alive==True:
            try:
                main2()
            except:

                servicemanager.LogErrorMsg(traceback.format_exc())


if __name__=='__main__':
    if len(sys.argv)==1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(TradingService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(TradingService)



#Function that starts the process of calling necessary functions
def main2():
  global login
  login=22334134
  global password
  password="5(jt0MqVowo!"
  global server
  server="Forex.com-Demo 535"
  terminalconnect(login,password,server)
  openTrades()
  createsocket()

#Function that creates the socket for communication
def createsocket():
     global sock
     global msd
     sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
     sock.bind(("",2023))
     sock.listen()
     print("socket is listening")
     while True:
        t1=threading.Thread(target=createThread,args=(sock,))
        t1.start()
        time.sleep(10)
        

#Function which creates seperate socket for sending and recieiving msg's
def createThread(sock):
    try:
        #recieve incoming information from Forex.com
        conn, addr=sock.accept()
        print("socket accepts the connection")
        conn.send("finally working".encode())
        msd=str(conn.recv(1024).decode('utf-8'))
        
        #filtering the recieved message to get ATR and pair information
        _=re.split(r"\x00",msd)[0:-1]
        print(_)
        ATR=round(float(_[0]),4)
        pair=_[1]
        position=_[-1]
        tradeLibrary(pair,position,ATR)
        #create Thread for calling next function
        t2=threading.Thread(target=trade_manager,args=(pair,ATR,position,))
        t2.start()
        time.sleep(1)
    except:
        servicemanager.LogErrorMsg(traceback.format_exc())

#Function which accesses created document containing open trades
def tradeLibrary(pair,position,ATR):
    #open and recording values into document
    file=open('tradingreport.txt',mode='r+')
    currentTrades1=[]
    currentTrades2=['']
    for i in file.readlines():
        currentTrades1.append(i.split())
        currentTrades2.extend(i.split())
    try:
        #checks if theres a documented trade with that pair and deletes if there
        #is and rewrites document with the new trade appended in
        if currentTrades2.index(pair):
            currentTrades1.pop(int((currentTrades2.index(pair)-1)/3))
            servicemanager.LogInfoMsg(str(currentTrades1))
            file.seek(0)
            file.truncate()
            currentTrades1.append([''.join(pair),''.join(position),''.join(str(ATR))])
            file.write(tabulate.tabulate(currentTrades1,tablefmt='plain')+'\n')
            file.close()
    except ValueError:
        tradeInfo=[''.join(pair),''.join(position),''.join(str(ATR))]
        file=open('tradingreport.txt',mode='a+')
        file.write(tabulate.tabulate([tradeInfo],tablefmt='plain')+'\n')
        file.close()
#Function which analyzes open trades and reinitializes there trailing stop
def openTrades():
    file=open('tradingreport.txt',mode='r+')
    currentTrades1=[]
    currentTrades2=['']
    for i in file.readlines():
        currentTrades1.append(i.split())
        currentTrades2.extend(i.split())
      
    trade=mt5.positions_get()
    for i in trade:
        pair=i.symbol
        tickets=i.ticket
        if i.type==0:
            position='true'
        else:
            position='false'
        try:
            _=currentTrades2.index(pair)
            ATR=float(currentTrades1[int((_-1)/3)][2])
            dparsed=i.price_current
            servicemanager.LogInfoMsg(pair+position+str(ATR))
            tradeThread=threading.Thread(target=limits,
                                         args=(dparsed,ATR,tickets,pair,position))
            tradeThread.start()
        except ValueError:
            pass
        except:
            servicemanager.LogInfoMsg(traceback.format_exc())
        
#Function which connects to the metatrader 5 terminal
def terminalconnect(login,password,server):
  try:
      login=login
      password=password
      server=server
      account=mt5.login(login,password=password,server=server)
      initialize=mt5.initialize(login=login,password=password,server=server)
      servicemanager.LogInfoMsg(str(initialize))
      return initialize
  except:
        servicemanager.LogErrorMsg(traceback.format_exc())

#Function that gets the recent price and ticket number
def trade_manager(pair,ATR,position):
  tradeInfo=mt5.positions_info(pair)
  dparsed=_[0].price_current
  tickets=[tradeInfo[0].ticket,tradeInfo[1].ticket]
  limits(dparsed,ATR,tickets,pair,position)

#Function that sets the stoplosses and updates. Also handles takeprofit limits
def limits(dparsed,ATR,tickets,pair,position):
    if position=="true":
        lastPrice=dparsed
        while True:
            _=mt5.positions_get(symbol=pair)
            priceNow=_[0].price_current
            price_in=_[0].price_open
            takeprofit=price_in+(ATR*1)
            #check if takeprofit was hit
            try:
                if priceNow>takeprofit:
                    exitTrade=mt5.Close(pair,ticket=tickets[0])
                    tickets.pop(0)
                    
                #modify stoploss if price moved up
                else:
                    if priceNow>=lastPrice or priceNow<=lastPrice:
                        stoploss=priceNow-(ATR*1.5)
                        sl_request={"action":mt5.TRADE_ACTION_SLTP,"symbol":pair,
                        "sl":stoploss,"tp":0.000,"position":tickets}
                        sl=mt5.order_send(sl_request)
                        servicemanager.LogInfoMsg(str(sl))
                        lastPrice=priceNow
                        time.sleep(5)
            except:
                servicemanager.LogInfoMsg(traceback.format_exc())



    elif position=="false":
        lastPrice=dparsed
        while True:
            _=mt5.positions_get(symbol=pair)
            priceNow=_[0].price_current
            price_in=_[0].price_open
            takeprofit=price_in-(ATR*1)
            #check if takeprofit was hit
            try:
                if priceNow<takeprofit:
                    exitTrade=mt5.Close(pair,ticket=tickets[0])
                    tickets.pop(0)
                    tp=priceNow-ATR
                    #modify stoploss if price moved down
                else:
                    if priceNow<=lastPrice:
                        stoploss=priceNow+(ATR*1.5)
                        sl_request={"action":mt5.TRADE_ACTION_SLTP,"symbol":pair,"sl":stoploss,"tp":tp,
                        "position":ticket}
                        sl=mt5.order_send(sl_request)
                        lastPrice=priceNow
                        time.sleep(60)
            except:
                servicemanager.LogInfoMsg(traceback.format_exc())



#Function that closes the socket connection
def closesocket():
   scHandle=servicemanager.OpenSCManager(None,None,0xF003F)
   serviceHandle=servicemanager.OpenService(scHandle,"SL_TP_EA",
                                            0xF01FF)
   if win32service.CloseServiceHandler(serviceHandle):
      global sock
      sock.close()
      file.close()
      return("socket is closed")
