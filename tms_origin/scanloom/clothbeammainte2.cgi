#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSjavascript;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_CLOTH_BEAM_MAINTENANCE	= &TMSstr::get_str( 'CLOTH_BEAM_MAINTENANCE'	);

my $str_UPDATE_SETTING		= &TMSstr::get_str( 'UPDATE_SETTING'		);
my $str_UPDATE_OK		= &TMSstr::get_str( 'UPDATE_OK'			);

my $str_LOOM_NAME		= &TMSstr::get_str( "LOOM_NAME"			);
my $str_STYLE_NAME		= &TMSstr::get_str( "STYLE_NAME"		);
my $str_BEAM_NAME		= &TMSstr::get_str( "BEAM_NAME"			);

my $str_SHRINKAGE		= &TMSstr::get_str( 'SHRINKAGE'			);
my $str_UPPER_BEAM		= &TMSstr::get_str( 'UPPER_BEAM'		);
my $str_LOWER_BEAM		= &TMSstr::get_str( 'LOWER_BEAM'		);
my $str_BEAM			= &TMSstr::get_str( 'BEAM'			);
my $str_SET_LENGTH		= &TMSstr::get_str( 'SET_LENGTH'		);
my $str_DOFF_LENGTH		= &TMSstr::get_str( 'DOFF_LENGTH'		);
my $str_USE_EACH_DOFF_LENGTH	= &TMSstr::get_str( 'USE_EACH_DOFF_LENGTH'	);

my $str_YES			= &TMSstr::get_str( 'YES'			);
my $str_NO			= &TMSstr::get_str( 'NO'			);

my $str_CLOTH			= &TMSstr::get_str( 'CLOTH'			);
my $str_CLOTH_LENGTH		= &TMSstr::get_str( 'CLOTH_LENGTH'		);
my $str_BEAM_REMAIN		= &TMSstr::get_str( 'BEAM_REMAIN'		);

my $str_CORRECT_CLOTH_LENGTH	= &TMSstr::get_str( 'CORRECT_CLOTH_LENGTH'	);
my $str_CORRECT_BEAM_REMAIN	= &TMSstr::get_str( 'CORRECT_BEAM_REMAIN'	);

my $str_BACK			= &TMSstr::get_str( "BACK"			);

################################################################

my $html = new CGI;

my $mac_id = $html->param('mac_id');

my $mac_name        = "";
my $style           = "";
my $use_doff_length = 0;
my $doff_length     = 0;
my $beam            = "";
my $beam_set        = 0;
my $beam_shrinkage  = 0;
my $ubeam_ari       = 0;
my $ubeam           = "";
my $ubeam_set       = 0;
my $ubeam_shrinkage = 0;

## スキャナーの設定ファイルから、必要な設定を読み出し
my @loom_set = &TMSscanner::get_loom_setting( "mac_name",
                                              "style",
                                              "use_doff_length",
                                              "doff_length",
                                              "beam",
                                              "beam_set",
                                              "beam_shrinkage",
                                              "ubeam_ari",
                                              "ubeam",
                                              "ubeam_set",
                                              "ubeam_shrinkage" );

foreach(@loom_set){
  if( $$_[0] eq $mac_id ){

    ( $mac_id,
      $mac_name,
      $style,
      $use_doff_length,
      $doff_length,
      $beam,
      $beam_set,
      $beam_shrinkage,
      $ubeam_ari,
      $ubeam,
      $ubeam_set,
      $ubeam_shrinkage ) = @$_;
    
    last;
  }
}

if( length($mac_name) <= 0 ){ $mac_name = $mac_id; }  # 機台名無しの場合は、機台ID表示


#### 単位の読み込み ####

my $cloth_unit;
my $beam_unit;
my $density_unit;  # dummy

&TMSscanner::get_unit_setting( \$cloth_unit, \$beam_unit, \$density_unit );

my @str_LENGTH_UNIT = &TMSscanner::get_str_length_unit();


## 現在データを取得 ####

my $cloth_length = 0;
my $beam_remain  = 0;
my $ubeam_remain = 0;

my @data = ();
if( $mac_id =~ m/S([1-5])-([0-9]+)\.([0-9]+)/ ){
  my $scan_no = $1;
  my $filename = sprintf("%02d%03d.txt",$2,$3);
  @data = &TMSscanner::get_scanner_file( $scan_no, "data/status/$filename" );
}

if( $cloth_unit == 1 ){ # meter
  foreach my $line (@data){
    if(    $line =~ m/^Cloth_length_meter=(.+)/         ){ $cloth_length = $1; }
    elsif( $line =~ m/^Remaining_Length_meter=(.+)/     ){ $beam_remain  = $1; }
    elsif( $line =~ m/^Top_remaining_Length_meter=(.+)/ ){ $ubeam_remain = $1; }
  }
}
elsif( $cloth_unit == 2 ){  # yard
  foreach my $line (@data){
    if(    $line =~ m/^Cloth_length_yard=(.+)/          ){ $cloth_length = $1; }
    elsif( $line =~ m/^Remaining_Length_yard=(.+)/      ){ $beam_remain  = $1; }
    elsif( $line =~ m/^Top_remaining_Length_yard=(.+)/  ){ $ubeam_remain = $1; }
  }
}
else{ # pick
  foreach my $line (@data){
    if(    $line =~ m/^Cloth_length_pick=(.+)/          ){ $cloth_length = sprintf("%.1f",$1/1000); }
    elsif( $line =~ m/^Remaining_Length_meter=(.+)/     ){ $beam_remain  = $1; }
    elsif( $line =~ m/^Top_remaining_Length_meter=(.+)/ ){ $ubeam_remain = $1; }
  }
}

#### スキャナー１からスタイルマスタを取得 ####

my @style_mst = &TMSscanner::get_scanner_file( 1, "set/style_mst.txt" );

my @style_option = (["",""]);
foreach(@style_mst){
  my ($name,$density,$style_doff_len) = split(/\t/);
  push( @style_option,[$name,"$name ( $style_doff_len$str_LENGTH_UNIT[$cloth_unit] )"] );
}


##########################################################################

my $tbl_width = 630;

my $title = $str_CLOTH_BEAM_MAINTENANCE;
my $cgifile = 'clothbeammainte3.cgi';
my $menu_color = '#fdb913';
my $body_color = '#fff2dd';
my $submit_button = $str_UPDATE_SETTING;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n";

print	"  function off_useDoffLength() {\n".
	"    document.fminput.use_doff_length[0].checked = true;\n".
	"  }\n";

print &TMSjavascript::checkName();
print &TMSjavascript::checkNumber();

print	"  function checkSubmit(aForm) {\n".
	"    if( ! checkNumber(aForm.doff_length, 0, 99999) ){ return false; }\n".
	"    if( aForm.correct_cloth[1].checked == true ){\n".
	"      if( ! checkNumber(aForm.cloth_length, 0, 99999) ){ return false; }\n".
	"    }\n".
	"    if( checkName(aForm.beam) < 0 ){ return false; }\n".
	"    if( aForm.correct_beam[1].checked == true ){\n".
	"      if( ! checkNumber(aForm.beam_remain, 0, 99999) ){ return false; }\n".
	"    }\n".
	"    if( ! checkNumber(aForm.beam_set, 0, 99999) ){ return false; }\n".
	"    if( ! checkNumber(aForm.beam_shrinkage, -30, 30) ){ return false; }\n".
	"\n";

if( $ubeam_ari == 1 ){ # ２重ビームの場合
  print	"    if( checkName(aForm.ubeam) < 0 ){ return false; }\n".
	"    if( aForm.correct_ubeam[1].checked == true ){\n".
	"      if( ! checkNumber(aForm.ubeam_remain, 0, 99999) ){ return false; }\n".
	"    }\n".
	"    if( ! checkNumber(aForm.ubeam_set, 0, 99999) ){ return false; }\n".
	"    if( ! checkNumber(aForm.ubeam_shrinkage, -30, 30) ){ return false; }\n".
	"\n";
}
print	"    return confirm(\"$str_UPDATE_OK\");\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n";

print	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return checkSubmit(this);\">\n";

print	"<table border=1 frame=box width=$tbl_width cellpadding=6>\n".
	"<tr align=center bgcolor=$menu_color><th><font size=+2 color=white>$title</font></th></tr>\n".
	"<tr align=center bgcolor=$body_color><td><br>\n";

print	"<table border=1 width=80% cellspacing=0 cellpadding=2>\n";


print	"<tr><th nowrap colspan=2>$str_LOOM_NAME</th>\n".
	"<td><input type=hidden name=\"mac_id\" value=\"$mac_id\"><B>$mac_name</B></td></tr>\n";

print	"<tr><th nowrap colspan=2>$str_STYLE_NAME ($str_DOFF_LENGTH)</th>\n".
	"<td><select name=\"style\" onChange=\"off_useDoffLength()\">\n";
&print_style_option($style,\@style_option);
print	"</select></td></tr>\n";

my @checked = ("","");
if( $use_doff_length ){ $checked[1] = "checked"; } 
else{                   $checked[0] = "checked"; } 

print	"<tr><th nowrap colspan=2>$str_USE_EACH_DOFF_LENGTH</th>\n".
	"<td><input type=radio name=\"use_doff_length\" value=\"0\" $checked[0]>$str_NO<BR>\n".
	"<input type=radio name=\"use_doff_length\" value=\"1\" $checked[1]>$str_YES\n".
	"<input type=text name=\"doff_length\" value=\"$doff_length\" size=5>$str_LENGTH_UNIT[$cloth_unit]</td></tr>\n";

print	"\n<TR><TD colspan=3>&nbsp;</TD></TR>\n";

### クロス設定 ###
print	"<tr><th rowspan=2>$str_CLOTH</th>\n".
	"<th>$str_CLOTH_LENGTH</th><td>$cloth_length $str_LENGTH_UNIT[$cloth_unit]</td></tr>\n";

print	"<tr><th>$str_CORRECT_CLOTH_LENGTH</th>\n".
	"<td><input type=radio name=\"correct_cloth\" value=\"0\" checked>$str_NO<BR>\n".
	"<input type=radio name=\"correct_cloth\" value=\"1\">$str_YES\n".
	"<input type=text name=\"cloth_length\" value=\"$cloth_length\" size=5 onChange=\"javascript:document.fminput.correct_cloth[1].checked=true;\">$str_LENGTH_UNIT[$cloth_unit]</td></tr>\n";

### 上ビーム設定 ###
if( $ubeam_ari ){
  print	"\n<TR><TD colspan=3>&nbsp;</TD></TR>\n";

  print	"<tr><th rowspan=5>$str_UPPER_BEAM</th>\n".
	"<th>$str_BEAM_REMAIN</th><td>$ubeam_remain $str_LENGTH_UNIT[$beam_unit]</td></tr>\n";

  if( $ubeam_remain < 0 ){ $ubeam_remain = 0; }
  print	"<tr><th>$str_CORRECT_BEAM_REMAIN</th>\n".
	"<td><input type=radio name=\"correct_ubeam\" value=\"0\" checked>$str_NO<BR>\n".
	"<input type=radio name=\"correct_ubeam\" value=\"1\">$str_YES\n".
	"<input type=text name=\"ubeam_remain\" value=\"$ubeam_remain\" size=8 onChange=\"javascript:document.fminput.correct_ubeam[1].checked=true;\">$str_LENGTH_UNIT[$beam_unit]</td></tr>\n";

  print	"<tr><th>$str_BEAM_NAME</th>\n".
	"<td><input type=text name=\"ubeam\" value=\"$ubeam\" size=15></td></tr>\n";

  print	"<tr><th>$str_SET_LENGTH</th>\n".
	"<td><input type=text name=\"ubeam_set\" value=\"$ubeam_set\" size=8>$str_LENGTH_UNIT[$beam_unit]</td></tr>\n";

  print	"<tr><th>$str_SHRINKAGE</th>\n".
	"<td><input type=text name=\"ubeam_shrinkage\" value=\"$ubeam_shrinkage\" size=6>%</td></tr>\n";
}else{
  print "\n".
	"<input type=hidden name=\"ubeam\" value=\"$ubeam\">\n".
	"<input type=hidden name=\"correct_ubeam\" value=\"0\">\n".
	"<input type=hidden name=\"ubeam_remain\" value=\"0\">\n".  # この設定は無視される
	"<input type=hidden name=\"ubeam_set\" value=\"$ubeam_set\">\n".
	"<input type=hidden name=\"ubeam_shrinkage\" value=\"$ubeam_shrinkage\">\n";
}

print	"\n<TR><TD colspan=3>&nbsp;</TD></TR>\n";

### 下ビーム設定 ###
print	"<tr><th rowspan=5>";
if( $ubeam_ari ){ print $str_LOWER_BEAM; }
else{             print $str_BEAM;       }
print	"</th>\n".
	"<th>$str_BEAM_REMAIN</th><td>$beam_remain $str_LENGTH_UNIT[$beam_unit]</td></tr>\n";

if( $beam_remain < 0 ){ $beam_remain = 0; }
print	"<tr><th>$str_CORRECT_BEAM_REMAIN</th>\n".
	"<td><input type=radio name=\"correct_beam\" value=\"0\" checked>$str_NO<BR>\n".
	"<input type=radio name=\"correct_beam\" value=\"1\">$str_YES\n".
	"<input type=text name=\"beam_remain\" value=\"$beam_remain\" size=8 OnChange=\"javascript:document.fminput.correct_beam[1].checked=true;\">$str_LENGTH_UNIT[$beam_unit]</td></tr>\n";

print	"<tr><th>$str_BEAM_NAME</th>\n".
	"<td><input type=text name=\"beam\" value=\"$beam\" size=15></td></tr>\n";

print	"<tr><th>$str_SET_LENGTH</th>\n".
	"<td><input type=text name=\"beam_set\" value=\"$beam_set\" size=8>$str_LENGTH_UNIT[$beam_unit]</td></tr>\n";

print	"<tr><th>$str_SHRINKAGE</th>\n".
	"<td><input type=text name=\"beam_shrinkage\" value=\"$beam_shrinkage\" size=6>%</td></tr>\n";

print	"</table>\n";
print	"<br></td></tr>\n";

#### submit ボタン ####
print	"<tr><td align=center bgcolor=$body_color colspan=9>\n".
	"<input type=button name=\"back\" value=\"$str_BACK\" onClick=\"javascript:history.back()\"> &nbsp; \n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

#####################################################################################

sub print_style_option
{
  my ($style,$r_option) = @_;

  # 設定されているスタイルが、スタイルマスタに在るか調べる
  if( $style ne "" ){
    my $match_flg = 0;
    foreach(@$r_option){
      my( $val,$str) = @$_;
      if( $style eq $val ){ $match_flg = 1; last; }
    }
    if( $match_flg == 0 ){  # 存在しない場合赤字で表示
      print "<option value=\"$style\" style=\"color=red\" selected>$style</option>\n";
    }
  }

  # ここから本番
  my $match_flg = 0;
  foreach(@$r_option){
    my( $val,$str) = @$_;

    if( $match_flg == 0 ){
      if( $style eq $val ){
        print "<option value=\"$val\" selected>$str</option>\n";
        $match_flg = 1;  # 一致が複数在っても、selected は先頭の１回だけ
        next;
      }
    }
    print "<option value=\"$val\">$str</option>\n";
  }
}

