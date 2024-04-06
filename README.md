
<h1>
  Welcome to the TradingEA project
</h1>

<h2>
  Purpose:
</h2>

<p1>
  An autonomous trading helper which allows participant in the financial markets to 
  manage their money more reliably and efficiently.
</p1> 

<h3>
  Programming applications:
</h3>

<p>
  This project utiizes python for developing server side operation and mql5 for client side operations. Mql5 is the official langugae for the Metatrader5 platform for creating various trading tools.
</p>

<div>
<h4 >
  <strong>Avaliability:</strong>
</h4>

<p>
  This product is specific to the MetaTrader5 platform, however it can be applied to various brokers which offer this platform for trade analysis.
</p>
<image height=100% width=50% src="https://1000logos.net/wp-content/uploads/2020/08/Python-Logo.png">
<image height=100% width=50% src='https://c.mql5.com/i/docs/background_docs_2x.png'>
</image>
<br>
</div>

<h4 style='font-size=100px;'>
  Installation
</h4>

<p>
  In order to use this AI it important to download the combinedalgoAI mq5 file and sl_tp_ea python file into yor local machine. The combinedalgoAI file must be added into the experts folder in your Metatrader5  directory. The python script can be run on the command line or python IDE. 
</p>

<h4>
  Important information:
  <br></br>
<li>IP address: Found through the commands <i>ipconfig</i> on windows or <i>ifconfig</i> on linux and MAC  command line interface </li>
<li>login and password for MetaTrader 5 account</li>
</h4>



<h5>
Adding as a Windows service:
<br></br>
<p>
  The python script can be run as a Windows service, meaning run as a continous background service. In order to do so you must run the the following command "python <i>servicename</i> --startup auto install". The default service name is SL_TP_EA however if you do change that make sure to update it. You can then start the service using "python <i>servicename</i> start". Use the pywin32 API specifically win32serviceutil module in order to more infomation on manipulating service using command line interface. The service is not offered as a linux background process however this will come in the future. 
</p>
</h5>
<style>
  h5 {
    font-size:100px;
    font-weight:bold;
    }
</style>

