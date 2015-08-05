
try:
	import tempfile
	from threading import Thread
	from lib.active.osscan import OsScan
	from lib.active.pingscan import PingScan
	from lib.active.portscan import PortScan
	from lib.core.core import Core,InitDirFile
	from lib.active.scriptscan import ScriptScan
except ImportError, err:
	from lib.core.core import Core
	Core.print_error(err)


class ActiveScan(InitDirFile):

	def __init__(self, args):

		self.__args = args
		InitDirFile.__init__(self, [Core._commands_path["nmap"]], self.__args, "nmap")	
		
                self.__ip_file_to_scan = tempfile.NamedTemporaryFile(mode='w+t')


	def _run(self, logger):

		logger._logging("Flashlight active scan started")	

                PingScan(self.__args.destination, self._output_dir, self.__args.nmap_optimize, "PingScan")._run(self.__ip_file_to_scan, logger)  if self.__args.is_alive else self.__ip_file_to_scan.write("\n".join([ip.strip() for ip in self.__args.destination.split(",")]))

		port_scan = PortScan(self.__args.config_file, self._output_dir, self.__ip_file_to_scan, self.__args.nmap_optimize, "PortScan")
                os_scan = OsScan(self._output_dir, self.__ip_file_to_scan, self.__args.nmap_optimize, "OsScan")
                script_scan = ScriptScan(self.__args.config_file, self._output_dir, self.__ip_file_to_scan, self.__args.nmap_optimize, "ScriptScan")

                thread_list = []
                try:
                        for counter, func in enumerate(( port_scan, os_scan, script_scan)):
                                thread_number = "t_{0}".format(counter)
                                thread_number = Thread(target = func._run, args = (logger,))
                                thread_number.start()
                                thread_list.append(thread_number)

                        for t in thread_list:
                                t.join()

			logger._logging("Flashlight active scan finished successfully")
                except Exception, err:
                        Core.print_error(err)

