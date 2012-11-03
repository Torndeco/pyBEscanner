#region

using System;
using System.Net;
using System.Threading;
using System.Diagnostics;
using BattleNET;

#endregion

namespace BattleNET_client
{
    internal class Program
    {
        private static void Main(string[] args)
        {
            Console.Title = "DayZ Ultra Server Restart";
            
            BattlEyeLoginCredentials loginCredentials = new BattlEyeLoginCredentials();
            #region
            loginCredentials.Host = "CHANGEME";
            loginCredentials.Port = 2302;
            loginCredentials.Password = "CHANGEME";
            #endregion
            // path to your server start up batch file
            string processPath = @"C:\dayz\TAKE4\server.bat";
            
            // title of your arma2server.exe
            string serverTitle = "ArmA 2 OA Console version 1.62 : port 2302";

            Console.Title += string.Format(" - {0}:{1}", loginCredentials.Host, loginCredentials.Port);

            

            IBattleNET b = new BattlEyeClient(loginCredentials);
            b.MessageReceivedEvent += DumpMessage;
            b.DisconnectEvent += Disconnected;
            b.ReconnectOnPacketLoss(true);
            b.Connect();

            if (b.IsConnected() == false)
            {
                Console.WriteLine("No connection starting server");
                Console.WriteLine("Bringing up server");
                Process.Start(processPath);
                return;
            }

            b.SendCommandPacket(EBattlEyeCommand.loadBans);
            Thread.Sleep(10000); // wait 10 secs  for no reason...
            b.Disconnect();

        }
                
        private static void Disconnected(BattlEyeDisconnectEventArgs args)
        {
            Console.WriteLine(args.Message);
        }

        private static void DumpMessage(BattlEyeMessageEventArgs args)
        {
            Console.WriteLine(args.Message);
        }
    }
}