#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMScommon;

require '../common/http_header.pm';

my $html = new CGI;
my $mode = $html->param('mode');

my $title = 'Execute Debug Commmand';
my $cmd  = '';
my $cmd2 = '';

if( $mode eq 'copy_xlsdata' ){
  &TMScommon::make_dir("xlsdata");
  $cmd = 'COPY /Y C:\TMSDATA\xlsdata\*.* xlsdata\*.*';
}
elsif( $mode eq 'del_xlsdata' ){
  $cmd = 'DEL /Q /F xlsdata\*.*';
}
elsif( $mode eq 'copy_apache' ){
  &TMScommon::make_dir("apache");
  $cmd  = 'COPY /Y ..\..\..\conf\httpd.conf apache\*.*';
  $cmd2 = 'COPY /Y ..\..\..\logs\*.* apache\*.*';
}
elsif( $mode eq 'del_apache' ){
  $cmd = 'DEL /Q /F apache\*.*';
}

my $tbl_width = 630;
my $tbl_width2 = $tbl_width -30;

my $menu_color = '#FDB913';
my $body_color = '#FFF2DD';

print	"<html>\n".
	"<head>\n".
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color><th><font size=+2 color=white>$title</font></th></tr>\n".
	"<tr align=center bgcolor=$body_color><td>\n".
	"<BR><BR>\n".
	"<table width=400><tr><td>\n";

if( $cmd eq "" ){ # Menu
  print "<A HREF=\"exec.cgi?mode=copy_xlsdata\"><B>COPY /Y C:\\TMSDATA\\xlsdata\\*.* xlsdata\\*.*</B></A><BR><BR>\n".
	"<A HREF=\"exec.cgi?mode=del_xlsdata\"><B>DEL /Q /F xlsdata\\*.*</B></A><BR><BR>\n".
	"<A HREF=\"xlsdata\"><B>Link to xlsdata</B></A><BR><BR>\n";

  print "<hr><br>\n".
	"<A HREF=\"exec.cgi?mode=copy_apache\"><B>COPY /Y ..\\..\\..\\conf\\httpd.conf apache\\*.*<BR>\n".
					         "COPY /Y ..\\..\\..\\logs\\*.* apache\\*.*</B></A><BR><BR>\n".
	"<A HREF=\"exec.cgi?mode=del_apache\"><B>DEL /Q /F apache\\*.*</B></A><BR><BR>\n".
	"<A HREF=\"apache\"><B>Link to apache</B></A><BR><BR>\n";
} else{
  print	"<PRE>\n".
	"<B>$cmd</B>\n\n";
  system( $cmd );
  if( length($cmd2) > 0 ){ print "\n\n<B>$cmd2</B>\n\n"; system( $cmd2 ); }
  print	"</PRE>\n";
}
print	"</td></tr></table>\n".
	"<BR>\n".
	"<center><A HREF=\"javascript:history.back()\"><font size=+2><B>Back</B></font></A></center>\n".
	"<BR>\n".
	"</td></tr></table>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	"</center></body></html>\n";

