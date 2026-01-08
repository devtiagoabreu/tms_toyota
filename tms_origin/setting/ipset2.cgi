#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSipset;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_SETTING_RESULT		= &TMSstr::get_str( "SETTING_RESULT"		);
my $str_SETTING_SUCCEED		= &TMSstr::get_str( "SETTING_SUCCEED"		);
#my $str_NO_VALID_DATA_FOUND	= &TMSstr::get_str( "NO_VALID_DATA_FOUND"	);
my $str_MENU			= &TMSstr::get_str( "MENU"			);
my $str_BACK			= &TMSstr::get_str( "BACK"			);

my $html = new CGI;

## 機台のIPアドレス ########################################

my $total = $html->param('total');

my @ip_list = ();
for( my $i=0; $i<=$total; $i++ ){
  my @ip =  $html->param("ip$i");
  my $err = 0;

  if( length($ip[4]) <= 0 ){ $ip[4] = $ip[3]; }  # １個のIPだけの登録に対応 2006.1.25

  for( my $j=0; $j<=$#ip; $j++ ){
    $ip[$j] =~ s/\s//g;	# スペースを取り除く。
    if( length($ip[$j]) <= 0 ){ $err = 1; last; }
    if( $ip[$j] > 255 ){ $err = 1; last; }
  }
  if( $err ){ next; }
  if( $ip[3] > $ip[4] ){ my $tmp = $ip[3]; $ip[3] = $ip[4]; $ip[4] = $tmp; }
  push( @ip_list, sprintf("%03d %03d %03d %03d %03d",$ip[0],$ip[1],$ip[2],$ip[3],$ip[4]) );
}

if( $#ip_list >= 0 ){
  my @tmp_list = sort @ip_list;
  @ip_list = ();

  my @ip1 = split(/ /,$tmp_list[0]);
  for( my $i=1; $i<=$#tmp_list; $i++ ){
    my @ip2 = split(/ /,$tmp_list[$i]);

    if( ($ip1[0] == $ip2[0]) && ($ip1[1] == $ip2[1]) && ($ip1[2] == $ip2[2]) ){
      # サブネットが同じ場合
      if( ($ip1[4] +1) >= $ip2[3] ){
        if( $ip1[4] >= $ip2[4] ){ next; }	# @ip2 は無効
        else{ $ip1[4] = $ip2[4]; next; }	# @ip1 と @ip2 をマージ
      }
    }
    push( @ip_list, sprintf("%3d %3d %3d %3d %3d",$ip1[0],$ip1[1],$ip1[2],$ip1[3],$ip1[4]) );
    @ip1 = @ip2;
  }
  push( @ip_list, sprintf("%3d %3d %3d %3d %3d",$ip1[0],$ip1[1],$ip1[2],$ip1[3],$ip1[4]) );
}

&TMSipset::save_ip_set_list(\@ip_list);

## メモリーカード対応 ########################################

my $memcard_file = "..\\..\\tmsdata\\setting\\memcard.txt";
if( defined($html->param('use_memcard')) ){
  if( open( FILE, "> $memcard_file" ) ){
    print FILE "use_memcard ari\n";
    close(FILE);
  }
}
else{
  unlink($memcard_file);
}

## スキャナーのIPアドレス ########################################

my @ip = $html->param('scan1_ip');

my $scan1_ip = "";

if( ($ip[0] =~ m/^[0-9]+$/) and
    ($ip[1] =~ m/^[0-9]+$/) and
    ($ip[2] =~ m/^[0-9]+$/) and
    ($ip[3] =~ m/^[0-9]+$/) ){
  $scan1_ip = sprintf("%d.%d.%d.%d", $ip[0],$ip[1],$ip[2],$ip[3]);  # 0を取る為
}
&TMSscanner::save_scan1_ip_set($scan1_ip);

## 画面表示 ########################################

my $tbl_width = 630;
my $title = $str_SETTING_RESULT;
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n".
	"<tr align=center bgcolor=$body_color><td>\n".
	"<BR><BR><BR>\n";

#if( ($#ip_list >= 0) or (length($scan1_ip) > 0) ){
  print	"<font size=+2><B>$str_SETTING_SUCCEED</B></font>\n";
#} else{
#  print	"<font size=+2><B>$str_NO_VALID_DATA_FOUND</B></font>\n";
#}

print	"<BR><BR><BR>\n".
	"<NOBR>\n".
	"<A HREF=\"../\"><IMG SRC=\"../image/menu2_$lang.jpg\" width=85 height=27 alt=\"$str_MENU\" border=0></A>\n".
	"<A HREF=\"ipset.cgi\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
	"</NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

