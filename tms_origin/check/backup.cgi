#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMScommon;

require '../common/http_header.pm';


# 旧バージョンの fixlistフォルダを削除
my $shift_fix_dir    = "..\\..\\tmsdata\\shift\\fixlist";
my $operator_fix_dir = "..\\..\\tmsdata\\operator\\fixlist";

if( -d $shift_fix_dir ){
  # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
  system( "del /Q /F $shift_fix_dir\\*.*" );
  rmdir( $shift_fix_dir );
}
if( -d $operator_fix_dir ){
  # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
  system( "del /Q /F $operator_fix_dir\\*.*" );
  rmdir( $operator_fix_dir );
}


# 古いBACKUPファイルを削除
if( -f 'tmsdata.tgz' ){ unlink( 'tmsdata.tgz' ); }
if( -f 'tmsdata.zip' ){ unlink( 'tmsdata.zip' ); }

# (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
system( 'cd ..\.. & tms\bin\zip.exe -q -r tms\check\tmsdata tmsdata\current tmsdata\shift tmsdata\operator tmsdata\setting tmsdata\stop_history' );

my $tbl_width = 630;
my $tbl_width2 = $tbl_width -30;

my $title = 'Data Backup & Download';
my $menu_color = '#FDB913';
my $body_color = '#FFF2DD';

print	"<html>\n".
	"<head>\n".
	&TMScommon::meta_no_cache_tag().
#	"<META HTTP-EQUIV=\"Refresh\" CONTENT=\"0; URL=tmsdata.zip\">\n".
	"<title>$title</title>\n".
	"</head>\n".
#	"<body bgcolor=#C7C4E2 onLoad=\"setTimeout('history.back()',15000)\">\n".
	"<body bgcolor=#C7C4E2>\n".
	"<center>\n".
	"<BR><BR>\n".
	"<B><font size=+1>$title</font></B>\n".
	"<BR><BR><BR>\n".
	"<a href=\"tmsdata.zip\"><B><font size=+1>tmsdata.zip</font></B> (Download Here)</a>".
	"<BR><BR><BR>\n".
	"<a href=\"javascript:history.back()\"><B><font size=+1>&lt; Back &gt;</font></B></a>".
	"</center>\n".
	"</BODY></HTML>\n";

