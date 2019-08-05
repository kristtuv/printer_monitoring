#!python3
"""
Program is used to generate the .py versions of the mibs
which are used py pysnmp.
This files should already be generated and can be found
in the directory name equal to the dstdirectory name
found in config.py.
If the directory exist and you are not adding any new mibs
there should not be any reason for you to run this program.
"""
from pysmi.reader import getReadersFromUrls
from pysmi.searcher import PyFileSearcher, PyPackageSearcher
from pysmi.writer import PyFileWriter
from pysmi.parser import SmiV1CompatParser
from pysmi.codegen import PySnmpCodeGen
from pysmi.compiler import MibCompiler

from config import dstdirectory, mibpaths
# debug.setLogger(debug.Debug('all'))

class MibDump:
    def __init__(self,
                 inputmibs=['Printer-MIB','SNMPv2-MIB','DISMAN-EVENT-MIB'],
                 mibpaths=mibpaths,
                 dstdirectory=dstdirectory,
                 searchers=[]):
        
        #General mibs + usr defined mibs
        mibsources = ['/usr/share/snmp/mibs', 'http://mibs.snmplabs.com/asn1/@mib@']
        mibsources += mibpaths

        #Defining standards pysnmp mib files ('pysnmp.smi.mibs', 'pysnmp_mibs')
        #Define searchers which finds existing compiled files and skips them
        mibsearchers = PySnmpCodeGen.defaultMibPackages
        searchers += [PyFileSearcher(dstdirectory)]
        searchers += [PyPackageSearcher(mibsearcher) for mibsearcher in mibsearchers]

        mibcompiler = MibCompiler(SmiV1CompatParser(),
                                  PySnmpCodeGen(),
                                  PyFileWriter(dstdirectory))

        #getReaderFromUrls uses pysmi.reader.localfile.FileReader
        #and pysmi.reader.httpclient.HttpReader to add the Sources
        #and urllib.parse to check wheter link is file or http.
        #This is a quick way of adding the sources
        mibcompiler.addSources(*getReadersFromUrls(*mibsources))
        mibcompiler.addSearchers(*searchers)
        mibcompiler.compile(*inputmibs)

if __name__=='__main__':
    MibDump()
