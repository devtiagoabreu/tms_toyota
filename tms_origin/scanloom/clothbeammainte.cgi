#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_CLOTH_BEAM_MAINTENANCE	= &TMSstr::get_str( 'CLOTH_BEAM_MAINTENANCE'	);

################################################################

my $tbl_width = 630;
my $tbl_width2 = $tbl_width -30;

my $title = $str_CLOTH_BEAM_MAINTENANCE;
my $menu_color = '#FDB913';
my $body_color = '#FFF2DD';

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

# スキャナーの設定ファイルから、必要な設定を読み出し
my @loom_set = &TMSscanner::get_loom_setting( "mac_name" );

# 機台名が未設定の場合は、機台IDで表示
foreach(@loom_set){
  if( length($$_[1]) == 0 ){ $$_[1] = $$_[0]; }
}
## 機台名、機台ID順にソート
@loom_set = sort { "$$a[1] $$a[0]" cmp "$$b[1] $$b[0]" } @loom_set;

my @mac_name = ();
my @mac_id   = ();

for( my $i=0; $i<=$#loom_set; $i++ ){
  my ($id, $name) =  @{$loom_set[$i]};
  $mac_name[$i] = $name;
  $mac_id[$i]   = $id;
}

my $line = int(($#mac_name +1) / 5);
if( (($#mac_name +1) % 5) > 0 ){ $line += 1; }

for( my $i=0; $i<5; $i++ ){
  print	"<td align=center valign=top>\n";

  my $start = ($line * $i);
  my $end   = ($line * ($i+1));
  if( $end > ($#mac_name +1) ){ $end = ($#mac_name +1); }

  for( my $j=$start; $j<$end; $j++ ){
    print "&nbsp;<A HREF=clothbeammainte2.cgi?mac_id=$mac_id[$j]><B>$mac_name[$j]</B></A>&nbsp;<br>\n";
  }
  print	"</td>";

}

print	"</tr></table>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

