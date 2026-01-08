#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMScommon;
use TMSipset;
use TMSscanner;

require '../common/http_header.pm';

my $html = new CGI;
my $mode = $html->param('mode');

my $title = '';
my $url = '/';
my @scan_ip;

if( $mode eq 'monitor' ){
  $title = 'Show Loom TMS Data';
  $url = '/cgi-bin/ext.cgi?func=tms_get_monitor_data&data1=current&data2=monitor&data3=shift&data4=history';
}
elsif( $mode eq 'stat' ){
  $title = 'Show Loom Status Data';
  $url = '/cgi-bin/ext.cgi?func=get_stat';
}
elsif( $mode eq 'log' ){
  $title = 'Show Loom Log for TMS';
  $url = '/cgi-bin/ext.cgi?func=tms_log_request';
}
elsif( $mode eq 'scanner' ){
  $title = 'Link to TMS Scanner';
  $url = '/TmsScanner/';
  @scan_ip = &TMSscanner::get_scan_ip();  # エラー時に画面を出す為、ここで読み込む
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
	"<table width=$tbl_width2><tr>";

## ----- 機台のリスト -----
if( ($mode eq 'monitor') or 
    ($mode eq 'stat') or
    ($mode eq 'log') ){

  my @name_list = ();
  my @ip_list = &TMSipset::get_all_ip_list();
  &TMSipset::get_name_ip_list( \@name_list, \@ip_list );

  my $line = 0;
  if(    ($#name_list +1)%3 == 1 ){ $line = ($#name_list +3)/3; }
  elsif( ($#name_list +1)%3 == 2 ){ $line = ($#name_list +2)/3; }
  else{                             $line = ($#name_list +1)/3; }

  for( my $i=0; $i<3; $i++ ){
    print	"<td align=center valign=top>\n";

    my $start = ($line*$i);
    my $end   = ($line*($i+1));
    if( $end > ($#name_list +1) ){ $end = ($#name_list +1); }
    for( my $j=$start; $j<$end; $j++ ){
      my $name = $name_list[$j];
      my $ip   = $ip_list[$j];
      if( $ip eq $name ){
        print	"&nbsp;<A HREF=http://$ip$url target=\"LoomWindow\"><B><font size=+1>$name</font></B></A>&nbsp;<br>\n";
      } else{
        print	"&nbsp;<A HREF=http://$ip$url target=\"LoomWindow\"><B><font size=+1>$name</font></B>&nbsp;($ip)</A>&nbsp;<br>\n";
      }
    }
    print "</td>";

  }
}
## ----- スキャナーのリスト -----
elsif( $mode eq 'scanner' ){

  print "<td align=center><BR>\n";

  if( defined $scan_ip[0] ){  print "<A HREF=http://$scan_ip[0]$url>Scanner1 ($scan_ip[0])</A><BR><BR>\n"; }
  if( defined $scan_ip[1] ){  print "<A HREF=http://$scan_ip[1]$url>Scanner2 ($scan_ip[1])</A><BR><BR>\n"; }
  if( defined $scan_ip[2] ){  print "<A HREF=http://$scan_ip[2]$url>Scanner3 ($scan_ip[2])</A><BR><BR>\n"; }
  if( defined $scan_ip[3] ){  print "<A HREF=http://$scan_ip[3]$url>Scanner4 ($scan_ip[3])</A><BR><BR>\n"; }
  if( defined $scan_ip[4] ){  print "<A HREF=http://$scan_ip[4]$url>Scanner5 ($scan_ip[4])</A><BR><BR>\n"; }

  print "</td>\n";

}

## -------------------------

print	"</tr></table>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	"</center></body></html>\n";

