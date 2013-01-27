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
            
            BattlEyeLoginCredentials loginCredentials = new BattlEyeLoginCredentials();
            #region
			if (args.Length == 3)
			{
	            loginCredentials.Host = args[0];
	            loginCredentials.Port = Convert.ToInt32(args[1]);
	            loginCredentials.Password = args[2];
			}
			else
			{
				Console.WriteLine("Wrong Number of Args");
				Thread.Sleep(5000); 
				Environment.Exit(0);
			}
            #endregion
            

            BattlEyeClient b = new BattlEyeClient(loginCredentials);
            b.BattlEyeMessageReceived += BattlEyeMessageReceived;
			b.BattlEyeConnected += BattlEyeConnected;
            b.BattlEyeDisconnected += BattlEyeDisconnected;
            b.ReconnectOnPacketLoss = true;
            b.Connect();

            if (b.Connected)
            {
            	b.SendCommand(BattlEyeCommand.LoadBans);
				while (b.CommandQueue > 0) { /* wait until server received packet */ };
	            Thread.Sleep(1000); // wait 1 second  for no reason...
            }
			else
			{
                Console.WriteLine("Couldnt connect to server");
				Console.WriteLine("Failed to reload bans");
				Environment.Exit(0);
			}
            b.Disconnect();

        }
		
        private static void BattlEyeConnected(BattlEyeConnectEventArgs args)
        {
            //if (args.ConnectionResult == BattlEyeConnectionResult.Success) { /* Connected successfully */ }
            //if (args.ConnectionResult == BattlEyeConnectionResult.InvalidLogin) { /* Connection failed, invalid login details */ }
            //if (args.ConnectionResult == BattlEyeConnectionResult.ConnectionFailed) { /* Connection failed, host unreachable */ }

            Console.WriteLine(args.Message);
        }
                
        private static void BattlEyeDisconnected(BattlEyeDisconnectEventArgs args)
        {
            Console.WriteLine(args.Message);
        }

        private static void BattlEyeMessageReceived(BattlEyeMessageEventArgs args)
        {
            Console.WriteLine(args.Message);
        }
    }
}