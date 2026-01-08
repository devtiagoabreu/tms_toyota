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

my $str_CLOTH_BEAM_LIST_SETTING	= &TMSstr::get_str( 'CLOTH_BEAM_LIST_SETTING'	);

my $str_UPDATE_SETTING		= &TMSstr::get_str( 'UPDATE_SETTING'	);
my $str_UPDATE_OK		= &TMSstr::get_str( 'UPDATE_OK'		);

my $str_LOOM_NAME		= &TMSstr::get_str( "LOOM_NAME"		);
my $str_STYLE_NAME		= &TMSstr::get_str( "STYLE_NAME"	);
my $str_BEAM_NAME		= &TMSstr::get_str( "BEAM_NAME"		);

my $str_PAGE			= &TMSstr::get_str( 'PAGE'		);

my $str_SHRINKAGE		= &TMSstr::get_str( 'SHRINKAGE'		);
my $str_UPPER_BEAM		= &TMSstr::get_str( 'UPPER_BEAM'	);
my $str_LOWER_BEAM		= &TMSstr::get_str( 'LOWER_BEAM'	);
my $str_BEAM			= &TMSstr::get_str( 'BEAM'		);
my $str_SET_LENGTH		= &TMSstr::get_str( 'SET_LENGTH'	);

my $str_SETTING_RESULT		= &TMSstr::get_str( "SETTING_RESULT"	);
my $str_SETTING_SUCCEED		= &TMSstr::get_str( "SETTING_SUCCEED"	);
my $str_MENU			= &TMSstr::get_str( "MENU"		);
my $str_BACK			= &TMSstr::get_str( "BACK"		);

################################################################

## １ページの最大表示台数
use constant LOOM_DISP_MAX => 20;

my $html = new CGI;

my @loom_set;
my $beam_unit;
my $tmp_file;
my $org_style_file;


## 初めての表示（スキャナー設定ファイルから読み込み）
if( ! defined($html->param('tmp_file')) ){

  # スキャナーの設定ファイルから、必要な設定を読み出し
  @loom_set = &TMSscanner::get_loom_setting( "mac_name",
                                             "style",
                                             "use_doff_length",
                                             "beam",
                                             "beam_set",
                                             "beam_shrinkage",
                                             "ubeam_ari",
                                             "ubeam",
                                             "ubeam_set",
                                             "ubeam_shrinkage" );

  # 機台名が未設定の場合は、機台IDで表示
  foreach(@loom_set){
    if( length($$_[1]) == 0 ){ $$_[1] = $$_[0]; }
  }
  ## 機台名、機台ID順にソート
  @loom_set = sort { "$$a[1] $$a[0]" cmp "$$b[1] $$b[0]" } @loom_set;

  ## 単位設定読み出し
  my $length_unit;  ## ダミー
  my $density_unit; ## ダミー
  &TMSscanner::get_unit_setting( \$length_unit, \$beam_unit, \$density_unit );

  # 一時ファイル名を取得
  $tmp_file = &TMScommon::get_tmp_file_name("clothbeam");

  # 元々のスタイル設定を保存
  my @org_style = ();
  for( my $i=0; $i<=$#loom_set; $i++ ){
    my $style = ${$loom_set[$i]}[2];
    @{$org_style[$i]} = ($style);
  }
  $org_style_file = &TMScommon::get_tmp_file_name("org_style");
  &TMSscanner::save_tmp_file( $org_style_file, \@org_style );

}
## CGI パラメータから読み込み
else{

  # 設定前の値を一時ファイルから読み出し
  $tmp_file = $html->param('tmp_file');
  @loom_set = &TMSscanner::load_tmp_file($tmp_file);

  # 隠し設定を取得（長さ単位）
  $org_style_file = $html->param('org_style_file');
  $beam_unit      = $html->param('beam_unit');

  # 今回設定された値を読み出し
  my @set_mac_id          = $html->param('mac_id');
  my @set_style           = $html->param('style');
  my @set_beam            = $html->param('beam');
  my @set_beam_set        = $html->param('beam_set');
  my @set_beam_shrinkage  = $html->param('beam_shrinkage');
  my @set_ubeam           = $html->param('ubeam');
  my @set_ubeam_set       = $html->param('ubeam_set');
  my @set_ubeam_shrinkage = $html->param('ubeam_shrinkage');

  # 設定を上書きする
  foreach my $r_data (@loom_set){
    my $mac_id = $$r_data[0];
    for( my $i=0; $i<=$#set_mac_id; $i++ ){
      if( $mac_id eq $set_mac_id[$i] ){

        my $beam = $set_beam[$i];
        $beam =~ s/^\s+//g;  # 先頭のスペースを除去
        $beam =~ s/\s+$//g;  # 末尾のスペースを除去
        my $beam_set        = int($set_beam_set[$i]);
        my $beam_shrinkage  = sprintf("%.1f",$set_beam_shrinkage[$i]);

        my $ubeam = $set_ubeam[$i];
        $ubeam =~ s/^\s+//g;  # 先頭のスペースを除去
        $ubeam =~ s/\s+$//g;  # 末尾のスペースを除去
        my $ubeam_set       = int($set_ubeam_set[$i]);
        my $ubeam_shrinkage = sprintf("%.1f",$set_ubeam_shrinkage[$i]);

        @$r_data = ( $$r_data[0],      # mac_id   は更新しない
                     $$r_data[1],      # mac_name は更新しない
                     $set_style[$i],
                     $$r_data[3],      # use_doff_length は更新しない
                     $beam,
                     $beam_set,
                     $beam_shrinkage,
                     $$r_data[7],      # ubeam_ari は更新しない
                     $ubeam,
                     $ubeam_set,
                     $ubeam_shrinkage );
        last;
      }
    }
  }

  #### 設定完了時 ####
  if( defined($html->param('submit')) ){

    my @org_style = &TMSscanner::load_tmp_file($org_style_file);

    # スタイルを変更したら、use_doff_length を 0 にする
    for( my $i=0; $i<=$#loom_set; $i++ ){
      if( ${$loom_set[$i]}[2] ne ${$org_style[$i]}[0] ){  # style
        ${$loom_set[$i]}[3] = 0;  # use_doff_length
      }
    }

    &TMSscanner::update_loom_setting( \@loom_set,
                                      "",                # mac_name は更新しない
                                      "style",
                                      "",                # use_doff_length は更新しない
                                      "beam",
                                      "beam_set",
                                      "beam_shrinkage",
                                      "",                # ubeam_ari は更新しない
                                      "ubeam",
                                      "ubeam_set",
                                      "ubeam_shrinkage" );

    &disp_result_html();
    exit;
  }

}

## 上ビーム有りの機台が存在するか？
my $ubeam_system = (1==0);  # false

foreach my $r_data (@loom_set){
  if( $$r_data[7] == 1 ){
    $ubeam_system = (1==1);  # true
    last;
  }
}



## 一時ファイルに保存
&TMSscanner::save_tmp_file( $tmp_file, \@loom_set );


# スキャナー１からスタイルマスタを取得
my @style_mst = &TMSscanner::get_scanner_file( 1, "set/style_mst.txt" );

my @style_option = ("");
foreach(@style_mst){
  my ($name,$density,$doff_len) = split(/\t/);
  push( @style_option,$name );
}


## 表示するページの判断
my $page_max = ($#loom_set + 1) / LOOM_DISP_MAX;
if( $page_max > int($page_max) ){ $page_max = int($page_max) + 1; }

my $page = 1;
for( my $n=1; $n<=$page_max; $n++ ){
  if( defined($html->param("page$n")) ){
    $page = $n;
    last;
  }
}

## 表示対象のデータ範囲
my $disp_start = LOOM_DISP_MAX * ($page -1);
my $disp_end   = LOOM_DISP_MAX * $page;
if( $disp_end > ($#loom_set +1) ){ $disp_end = ($#loom_set +1); }

&disp_input_html();
exit;


##########################################################################

sub disp_input_html
{
my $tbl_width = 630;

my $title = $str_CLOTH_BEAM_LIST_SETTING;
my $cgifile = 'clothbeamset.cgi';
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

print &TMSjavascript::checkName();
print &TMSjavascript::checkNumber();

print	"  chkSubmit_flg = false;\n".
	"  function enableChkSubmit() {\n".
	"    chkSubmit_flg = true;\n".
	"  }\n".
	"  function checkSubmit(aForm) {\n".
	"    for( i=0; i<".($disp_end - $disp_start)."; i++ ){\n".
	"      if( checkName(aForm.beam[i]) < 0 ){ return false; }\n".
	"      if( ! checkNumber(aForm.beam_set[i], 0, 99999) ){ return false; }\n".
	"      if( ! checkNumber(aForm.beam_shrinkage[i], -30, 30) ){ return false; }\n".
	"\n".
	"      if( aForm.ubeam_ari[i].value == 1 ){\n". # ２重ビームの場合
	"        if( checkName(aForm.ubeam[i]) < 0 ){ return false; }\n".
	"        if( ! checkNumber(aForm.ubeam_set[i], 0, 99999) ){ return false; }\n".
	"        if( ! checkNumber(aForm.ubeam_shrinkage[i], -30, 30) ){ return false; }\n".
	"      }\n".
	"    }\n".
	"    if( chkSubmit_flg ){\n".
	"      chkSubmit_flg = false;\n".
	"      return confirm(\"$str_UPDATE_OK\");\n".
	"    }\n".
	"    return true;\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n";

print	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return checkSubmit(this);\">\n".
	"<table width=$tbl_width><tr><th><font size=+2>$title</font></th></tr></table>\n";

### 隠し設定 ###
print	"<input type=hidden name=\"tmp_file\" value=\"$tmp_file\">\n".
	"<input type=hidden name=\"org_style_file\" value=\"$org_style_file\">\n".
	"<input type=hidden name=\"beam_unit\" value=\"$beam_unit\">\n";

#### ページ切替ボタン ####
use constant PAGE_BUTTON_COLUMN_MAX => 5;

if( $page_max > 1 ){
  print	"<table cellpadding=2 cellspacing=2>\n";

  my $col_max;
  if( $page_max < PAGE_BUTTON_COLUMN_MAX ){ $col_max = $page_max; }
  else{ $col_max = PAGE_BUTTON_COLUMN_MAX; }

  my $n = 1;
  while( $n <= $page_max ){
    print "<tr align=center>\n";
    for (my $j=0; $j<$col_max; $j++ ){
      if( $n <= $page_max ){
        if( $n eq $page ){
          print "<td bgcolor=gray><input type=SUBMIT name=\"page$n\" value=\"$str_PAGE $n\" disabled></td>\n";
        }else{
          print "<td><input type=SUBMIT name=\"page$n\" value=\"$str_PAGE $n\"></td>\n";
        }
      }else{ print "<td></td>\n"; }
      ++$n;
    }
    print "</tr>\n";
  }
  print	"</table>\n";
}

#### 設定値タイトル ####
my @str_LENGTH_UNIT  = &TMSscanner::get_str_length_unit();

my $width = 630;
if( $ubeam_system ){ $width = 750; }
print	"<table border=1 frame=box width=$width cellpadding=1 cellspacing=1>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th nowrap rowspan=2><font color=white>$str_LOOM_NAME</font></th>\n".
	"<th nowrap rowspan=2><font color=white>$str_STYLE_NAME</font></th>\n".
	"<th nowrap colspan=3><font color=white>";
if( $ubeam_system ){ print $str_LOWER_BEAM; }
else{                print $str_BEAM;       }
print	"</font></th>\n";

if( $ubeam_system ){
  print	"<th nowrap colspan=3><font color=white>$str_UPPER_BEAM</font></th>\n";
}
print	"</tr>\n";
print	"<tr align=center bgcolor=$menu_color>\n".
	"<th nowrap><font color=white>$str_BEAM_NAME</font></th>\n".
	"<th nowrap><font color=white>$str_SET_LENGTH<BR>($str_LENGTH_UNIT[$beam_unit])</font></th>\n".
	"<th nowrap><font color=white>$str_SHRINKAGE<BR>(%)</font></th>\n";
if( $ubeam_system ){
  print	"<th nowrap><font color=white>$str_BEAM_NAME</font></th>\n".
	"<th nowrap><font color=white>$str_SET_LENGTH<BR>($str_LENGTH_UNIT[$beam_unit])</font></th>\n".
	"<th nowrap><font color=white>$str_SHRINKAGE<BR>(%)</font></th>\n";
}
print	"</tr>\n";

#### 設定値の入力 ####
for( my $i=$disp_start; $i<$disp_end; $i++ ){

  my ($mac_id,
      $mac_name,
      $style,
      $use_doff_length,  # dummy
      $beam,
      $beam_set,
      $beam_shrinkage,
      $ubeam_ari,
      $ubeam,
      $ubeam_set,
      $ubeam_shrinkage ) = @{$loom_set[$i]};

  # 機台名が未設定の場合は、機台IDで表示
  if( length($mac_name) == 0 ){ $mac_name = $mac_id; }

  print	"<tr align=center bgcolor=$body_color>\n".
	"<th><input type=hidden name=\"mac_id\" value=\"$mac_id\">$mac_name</th>\n";
  print	"<td><select name=\"style\">\n";
  &print_style_option($style,\@style_option);
  print	"</select></td>";

  print	"<td><input type=text name=\"beam\" value=\"$beam\" size=15></td>\n".
	"<td nowrap><input type=text name=\"beam_set\" value=\"$beam_set\" size=8></td>\n".
	"<td nowrap><input type=text name=\"beam_shrinkage\" value=\"$beam_shrinkage\" size=6>\n";

  print "<input type=hidden name=\"ubeam_ari\" value=\"$ubeam_ari\">\n";  # Javascript用に必要
  if( $ubeam_ari ){
    print "</td><td>\n".
	  "<input type=text name=\"ubeam\" value=\"$ubeam\" size=15></td>\n".
          "<td nowrap><input type=text name=\"ubeam_set\" value=\"$ubeam_set\" size=8></td>\n".
          "<td nowrap><input type=text name=\"ubeam_shrinkage\" value=\"$ubeam_shrinkage\" size=6></td>\n";
  }elsif( $ubeam_system ){
    print "</td><td><input type=hidden name=\"ubeam\" value=\"$ubeam\"></td>\n".
          "<td><input type=hidden name=\"ubeam_set\" value=\"$ubeam_set\"></td>\n".
          "<td><input type=hidden name=\"ubeam_shrinkage\" value=\"$ubeam_shrinkage\"></td>\n";
  }else{
    print "<input type=hidden name=\"ubeam\" value=\"$ubeam\">\n".
          "<input type=hidden name=\"ubeam_set\" value=\"$ubeam_set\">\n".
          "<input type=hidden name=\"ubeam_shrinkage\" value=\"$ubeam_shrinkage\">\n".
	  "</td>\n";
  }
  print "</tr>\n";
}

#### submit ボタン ####
print	"<tr><td align=center bgcolor=$body_color colspan=9>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\" onClick=\"enableChkSubmit()\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
}
#####################################################################################

sub print_style_option
{
  my ($style,$r_option) = @_;

  # 設定されているスタイルが、スタイルマスタに在るか調べる
  if( $style ne "" ){
    my $match_flg = 0;
    foreach(@$r_option){
      if( $style eq $_ ){ $match_flg = 1; last; }
    }
    if( $match_flg == 0 ){  # 存在しない場合赤字で表示
      print "<option value=\"$style\" style=\"color=red\" selected>$style</option>\n";
    }
  }

  # ここから本番
  my $match_flg = 0;
  foreach(@$r_option){
    if( $match_flg == 0 ){
      if( $style eq $_ ){
        print "<option value=\"$_\" selected>$_</option>\n";
        $match_flg = 1;  # 一致が複数在っても、selected は先頭の１回だけ
        next;
      }
    }
    print "<option value=\"$_\">$_</option>\n";
  }
}

#####################################################################

sub disp_result_html
{

my $tbl_width = 630;
my $title = $str_SETTING_RESULT;
my $menu_color = '#fdb913';
my $body_color = '#fff2dd';

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

  print	"<font size=+2><B>$str_SETTING_SUCCEED</B></font>\n";

print	"<BR><BR><BR>\n".
	"<NOBR>\n".
	"<A HREF=\"../\"><IMG SRC=\"../image/menu2_$lang.jpg\" width=85 height=27 alt=\"$str_MENU\" border=0></A>\n".
	"<A HREF=\"clothbeamset.cgi\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
	"</NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
}

#####################################################################
