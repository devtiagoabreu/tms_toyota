#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSlock;
use TMSselitem;

#require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $menu_color = '#426AB3';
my $body_color = '#E1E2F2';

my $html = new CGI;

my $sel_mode = $html->param('sel_mode');

my %loom  = ();
my %style = ();
if( $sel_mode eq 'loom' ){
  my @p = $html->param('loom');
  if( $#p < 0 ){
    require '../common/http_header.pm';
    print &TMScommon::no_data_page( $menu_color, $body_color );
    exit;
  }
  foreach(@p){ $loom{$_} = 1; }
} else{
  my @p = $html->param('style');
  if( $#p < 0 ){
    require '../common/http_header.pm';
    print &TMScommon::no_data_page( $menu_color, $body_color );
    exit;
  }
  foreach(@p){ $style{$_} = 1; }
}


my $period = $html->param('period');  # 期間種類
my @shift  = $html->param('shift');
@shift = sort @shift;

my @file = ();
my @index = ();
&TMScommon::get_shift_file_list( $period, \@shift, \@file, \@index );
                                # @file:  期間(@shift)にマッチするファイル名
                                # @index: 期間(@shift)の表示用文字列

my $update_lock = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::check_lockfile($update_lock,$ENV{REMOTE_ADDR},\$other_user) ){	# データ更新中は使用不可
  require '../common/http_header.pm';
  print &TMSlock::data_updating_page( $other_user );
  exit;
}

# 各ファイル名の取得
my $xlsfile  = "../xlsfile/ja/svsreport.xls";
if( $lang ne "ja" ){ $xlsfile  = "../xlsfile/en/svsreport.xls"; } # 日本語以外なら英語

my $datafile = &TMScommon::get_xlsdata_file_name("svsrepor","csv");

my $infofile = "svsrepor.tmshlp";


# ＣＳＶファイルの出力
my @val_color     = &TMSselitem::get_value_of_color();
my $val_beam_type = &TMSselitem::get_value_of_beam_type();


open(OUT, "> $datafile" );

my $now_date = &TMScommon::get_now_date();

print OUT	"( $now_date )\n".
		"$index[0] -> $index[$#index]\n".
		"\n";

print OUT &make_svsreport_title( $period, $val_beam_type, \@val_color );

my $dcount = 0;
for( my $i=0; $i<=$#file; $i++ ){
  my $f = $file[$i];
  open(IN,"< $f");
  while(<IN>){
    my $line = $_;
    my $m = 0;
    if( $sel_mode eq "loom" ){
      if( $line =~ m/,mac_name ([^,]+)/ ){
        if( exists($loom{$1}) ){ $m = 1; }
      }
    } else{  # "style"
      if( $line =~ m/,style ([^,]+)/ ){
        if( exists($style{$1}) ){ $m = 1; }
      }
    }

    if( $m ){
      $dcount++;
      print OUT &make_svsreport_data( $index[$i], \$line, $val_beam_type, \@val_color );
    }
  }
  close(IN);
}
close(OUT);


if( $dcount == 0 ){
  require '../common/http_header.pm';
  print &TMScommon::no_data_page( $menu_color, $body_color );
}
else{
  # TmsHelper.exe 用情報データ出力
  &TMScommon::http_header_tmsinf($infofile);

  print "method POPUP_EXCEL\n";
  print "version 1.0\n";

  print "xlsfile ". &TMScommon::get_fullpath_url($xlsfile). "\n";

  if( $ENV{REMOTE_ADDR} eq '127.0.0.1' ){  # ローカルの場合（データ読み込み高速化の為）
    print "csvfile1 ". &TMScommon::get_fullpath_file($datafile). "\n";
  }else{  # リモートの場合
    print "csvfile1 ". &TMScommon::get_fullpath_url($datafile). "\n";
  }

  #print "macro start_make_all\n";
}

exit;

###################################################################################################

sub make_svsreport_title
{
  my ( $period, $beam_type, $r_color_v ) = @_;

  my $line = 'STYLE,LOOM';

  my $period_type = 0;
  if(    $period eq "shift" ){ $period_type = 0; $line .= ",SHIFT"; }
  elsif( $period eq "date"  ){ $period_type = 1; $line .= ",DATE";  }
  elsif( $period eq "week"  ){ $period_type = 2; $line .= ",WEEK";  }
  elsif( $period eq "month" ){ $period_type = 3; $line .= ",MONTH"; }

  $line .= ',RUN&MINUTE,STOP&MINUTE,PRODUCT&PICK,EFFIC&PERCENT,RPM,WARP,WF1,WF2,OTHER,TOTAL';

  if( $beam_type == 2 ){
    $line .= ',WARP_TOP';
  }
  $line .= ',WARP_BOTTOM';

  # WF1
  for( my $i=0; $i<=$#$r_color_v; $i++ ){
    if( $$r_color_v[$i] ){ my $num = $i+1; $line .= ",WF1&COLOR$num"; }
  }
  # WF2
  for( my $i=0; $i<=$#$r_color_v; $i++ ){
    if( $$r_color_v[$i] ){ my $num = $i+1; $line .= ",WF2&COLOR$num"; }
  }


  my $param_key = "PARAM->,period_type";
  my $param_val = "VALUE->,$period_type";

  return $param_key."\n".
	 $param_val."\n".
	 "\n".
	 $line."\n";
}

###################################################################################################

sub make_svsreport_data
{
  my ( $index, $r_line, $beam_type, $r_color_v ) = @_;
 
  $$r_line =~ s/\n$//;		# 改行コードを削除。
# $$r_line =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
  my @list = split(/,/,$$r_line);

  my %tmp = ();
  foreach(@list){
    my @data = split(/ /,$_,2);
    if( $#data >= 1 ){ $tmp{$data[0]} = $data[1]; }
  }

  my $mac_name   = $tmp{"mac_name"};
  my $style_name = $tmp{"style"};
  my @seisan     = split(/ /,$tmp{"seisan"});
  my $run_tm     = $tmp{"run_tm"};
  my $stop_ttm   = $tmp{"stop_ttm"};
  my @stop_ct    = split(/ /,$tmp{"stop_ct"});
  my @wf1_ct     = split(/ /,$tmp{"wf1_ct"});
  my @wf2_ct     = split(/ /,$tmp{"wf2_ct"});
  my @lh_ct      = split(/ /,$tmp{"lh_ct"});

  # Ver3.0以前の旧データ対応
  if( $#stop_ct < 11 ){ $stop_ct[11] = 0; }  # CC後

  #### Create CSV Data ####

  my $pick = 1000 * $seisan[0];		# pick

  my $warp = $stop_ct[0] + $stop_ct[1];	# (0)WarpTop, (1)Warp

  my $wf1 = 0;
  foreach( @wf1_ct ){ $wf1 += $_; }	# ＷＦ１(カラー１～６)

  my $wf2 = 0;
  foreach( @wf2_ct ){ $wf2 += $_; }	# ＷＦ２(カラー１～６)

  my $other = 0;
  for( my $i=2; $i<=4; $i++ ){  # (2)False, (3)Leno(R), (4)Leno(L)
    $other += $stop_ct[$i];
  }
  $other += $stop_ct[11];	# (11)CC後
  foreach( @lh_ct ){ $other += $_; }	# 供給ミス(カラー１～６)

  my $total = $warp + $wf1 + $wf2 + $other;

  #### Create CSV Data ####

  my $htdata .=	"=\"$style_name\"".
		",=\"$mac_name\"".
		",$index".
		",$run_tm".
		",$stop_ttm".
		",$pick".	# pick
		",".		# effic <- Calc Excel
		",".		# rpm   <- Calc Excel
		",$warp".
		",$wf1".
		",$wf2".
		",$other".
		",$total";

  if( $beam_type == 2 ){
    $htdata .=	",$stop_ct[0]";	# Warp(upper)
  }
  $htdata .=	",$stop_ct[1]";	# Warp

  # WF1
  for( my $i=0; $i<=$#$r_color_v; $i++ ){
    if( $$r_color_v[$i] ){ $htdata .= ",$wf1_ct[$i]"; }
  }
  # WF2
  for( my $i=0; $i<=$#$r_color_v; $i++ ){
    if( $$r_color_v[$i] ){ $htdata .= ",$wf2_ct[$i]"; }
  }

  $htdata .= "\n";

  return $htdata;
}


