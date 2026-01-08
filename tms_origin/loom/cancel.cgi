#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $title     = &TMSstr::get_str( "CANCEL_PROCESSING" );
my $str_CLOSE = &TMSstr::get_str( "CLOSE" );

open(OUT, '> cancel.txt');
print OUT "CANCEL\n";
close(OUT);

print 	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2 onLoad=\"javascript:window.close()\">\n".
	"<center>\n".
	"<BR><BR><B>$title</B><BR><BR>\n".
	"<a href=\"javascript:window.close()\"><B><font size=+1>$str_CLOSE</font></B></a>".
	"</center>\n".
	"</BODY></HTML>\n";
