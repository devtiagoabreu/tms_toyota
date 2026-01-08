#! C:\Perl\bin\perl.exe

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Time::Local;

require '../common/http_header.pm';

print	"<html>\n".
	"<head>\n".
	"<meta http-equiv=\"cache-control\" content=\"no-cache\">\n".
	"<meta http-equiv=\"pragma\" content=\"no-cache\">\n".
	"<meta http-equiv=\"expires\" content=\"0\">\n".
	"</HEAD>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	"<table bgcolor=#FFF2DD border=1 cellpadding=4>\n".
	"<tr bgcolor=#FDB913>".
	"<th nowrap>Machine</th>".
	"<th nowrap>IP address</th>".
	"<th nowrap>SYS time</th>".
	"<th nowrap>RTC time</th>".
	"<th nowrap>PC time</th>".
	"<th nowrap>SYS-RTC</th>".
	"<th nowrap>SYS-PC</th>".
	"</tr>\n";

open(SETT, '< ../../tmsdata/current/setting.txt');
while(<SETT>){
  my @data = split(/,/);

  my $mac_name = "";
  my $ip_addr  = "";
  my $get_time = "";
  my $sys_time = "";
  my $rtc_time = "";

  foreach(@data){
    if(    m/^mac_name (.+)/ ){ $mac_name = $1; }
    elsif( m/^ip_addr (.+)/  ){ $ip_addr  = $1; }
    elsif( m/^get_time (.+)/ ){ $get_time = $1; }
    elsif( m/^sys_time (.+)/ ){ $sys_time = $1; }
    elsif( m/^rtc_time (.+)/ ){ $rtc_time = $1; }
  }

  my $sys = get_ymdhms($sys_time);
  my $rtc = get_ymdhms($rtc_time);
  my $get = get_ymdhms($get_time);

  my $sys_rtc = get_time2time($sys_time,$rtc_time);
  my $sys_get = get_time2time($sys_time,$get_time);

  print "<TR>".
	"<TD nowrap>$mac_name</TD>";

  if( $ip_addr =~ /^S/ ){  # スキャナーの場合
    print "<TD nowrap>$ip_addr</TD>";
  }else{
    print "<TD nowrap><A HREF=\"http://$ip_addr/\" target=\"LoomWindow\">$ip_addr</A></TD>";
  }
  print "<TD nowrap>$sys</TD>".
	"<TD nowrap>$rtc</TD>".
	"<TD nowrap>$get</TD>".
	"<TD nowrap>$sys_rtc</TD>".
	"<TD nowrap>$sys_get</TD>".
	"</TR>\n";
}
close(SETT);

print	"</table>\n".
	"</center></body></html>\n";

################################################################################

sub get_ymdhms
{
  my($time) = @_;

  my @d = split(/ /,$time);
  my $ymdhms = sprintf("%04d.%02d.%02d %02d:%02d:%02d", $d[0],$d[1],$d[2],$d[4],$d[5],$d[6]);
  return $ymdhms;
}

################################################################################

sub get_time2time
{
  my ($time1, $time2) = @_;
  my @data = ();

  @data = split(/ /,$time1);
  my $t1_date = timelocal($data[6],$data[5],$data[4],$data[2],($data[1] -1),($data[0] -1900));

  @data = split(/ /,$time2);
  my $t2_date = timelocal($data[6],$data[5],$data[4],$data[2],($data[1] -1),($data[0] -1900));

  my $diff = $t1_date - $t2_date;
  my $min = $diff/60;
  my $sec = (abs($diff)%60);

  my $t2t = sprintf( "%d:%02d",$min,$sec );

  if( ($diff < -120) || (120 < $diff) ){
    $t2t = "<font color=red><B>$t2t</B></font>";
  }

  return $t2t;
}

################################################################################
