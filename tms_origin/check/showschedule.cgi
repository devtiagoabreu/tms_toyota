#! C:\Perl\bin\perl.exe

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

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
	"<TH nowrap>Machine</TH>".
	"<TH nowrap>IP addrress</TH>".
	"<TH nowrap>SHIFT<BR>MODE</TH>".
	"<TH nowrap>SIMPLE</TH>".
	"<TH nowrap>DAY_0</TH>".
	"<TH nowrap>DAY_1</TH>".
	"<TH nowrap>DAY_2</TH>".
	"<TH nowrap>DAY_3</TH>".
	"<TH nowrap>DAY_4</TH>".
	"<TH nowrap>DAY_5</TH>".
	"<TH nowrap>DAY_6</TH>".
	"<TH nowrap>NAME_0</TH>".
	"<TH nowrap>NAME_1</TH>".
	"<TH nowrap>NAME_2</TH>".
	"<TH nowrap>NAME_3</TH>".
	"<TH nowrap>NAME_4</TH>".
	"<TH nowrap>NAME_5</TH>".
	"<TH nowrap>DAY<BR>START<BR>TIME</TH>".
	"</tr>\n";

open(SETT, '< ../../tmsdata/current/setting.txt');
while(<SETT>){
  my @item = split(/,/);

  my %val = ();
  foreach(@item){
    my @data = split(/ /,$_,2);
    $val{$data[0]} = $data[1];
  }

  my $ip_addr = $val{ip_addr};

  print "<TR>".
	"<TD nowrap>$val{mac_name}</TD>".
	"<TD nowrap><A HREF=\"http://$ip_addr/\" target=\"LoomWindow\">$ip_addr</A></TD>".
	"<TD nowrap>$val{SHIFT_MODE}</TD>".
	"<TD nowrap>". &shift_format($val{SIMPLE})."</TD>".
	"<TD nowrap>". &shift_format($val{DAY_0}). "</TD>".
	"<TD nowrap>". &shift_format($val{DAY_1}). "</TD>".
	"<TD nowrap>". &shift_format($val{DAY_2}). "</TD>".
	"<TD nowrap>". &shift_format($val{DAY_3}). "</TD>".
	"<TD nowrap>". &shift_format($val{DAY_4}). "</TD>".
	"<TD nowrap>". &shift_format($val{DAY_5}). "</TD>".
	"<TD nowrap>". &shift_format($val{DAY_6}). "</TD>".
	"<TD nowrap>$val{NAME_0}</TD>".
	"<TD nowrap>$val{NAME_1}</TD>".
	"<TD nowrap>$val{NAME_2}</TD>".
	"<TD nowrap>$val{NAME_3}</TD>".
	"<TD nowrap>$val{NAME_4}</TD>".
	"<TD nowrap>$val{NAME_5}</TD>".
	"<TD nowrap>$val{DAY_START_TIME}</TD>".
	"</TR>\n";
}
close(SETT);

print	"</table>\n".
	"</center></body></html>\n";

################################################################################

sub shift_format
{
  my ($shift) = @_;

  my @data = split(/ /,$shift);
  my $format = "";
  for( my $i=0; $i<$#data; $i++ ){
    $format .= "$data[$i]<BR>";
  }

  return $format;
}

################################################################################
