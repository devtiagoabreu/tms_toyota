#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSipset;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $tbl_width = 630;
my $tbl_width2 = $tbl_width -30;

my $menu_color = '#FDB913';
my $body_color = '#FFF2DD';

my $title = &TMSstr::get_str( "LINK_TO_LOOM_SCREEN" );

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color><th><font size=+2 color=white>$title</font></th></tr>\n".
	"<tr align=center bgcolor=$body_color><td>\n".
	"<table width=$tbl_width2><tr>";

my @name_list = ();
my @ip_list = &TMSipset::get_all_ip_list();
&TMSipset::get_name_ip_list( \@name_list, \@ip_list );

my $line = 0;
if(    ($#name_list +1)%3 == 1 ){ $line = int($#name_list +3)/3; }
elsif( ($#name_list +1)%3 == 2 ){ $line = int($#name_list +2)/3; }
else{                             $line = int($#name_list +1)/3; }

for( my $i=0; $i<3; $i++ ){
  print	"<td align=center valign=top>\n";

  my $start = ($line*$i);
  my $end   = ($line*($i+1));
  if( $end > ($#name_list +1) ){ $end = ($#name_list +1); }
  for( my $j=$start; $j<$end; $j++ ){
    my $name = $name_list[$j];
    my $ip   = $ip_list[$j];
    if( $ip eq $name ){
      print	"&nbsp;<A HREF=http://$ip/ target=\"LoomWindow\"><B><font size=+1>$name</font></B></A>&nbsp;<br>\n";
    } else{
      print	"&nbsp;<A HREF=http://$ip/ target=\"LoomWindow\"><B><font size=+1>$name</font></B>&nbsp;($ip)</A>&nbsp;<br>\n";
    }
  }
  print	"</td>";

}

print	"</tr></table>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

