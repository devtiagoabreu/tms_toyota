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

my $period = $html->param('period');
my @shift  = $html->param('shift');
@shift = sort @shift;

my @file = ();
my @index = ();
&TMScommon::get_shift_file_list( $period, \@shift, \@file, \@index );	# @file:  期間(@shift)にマッチするファイル名
									# @index: 期間(@shift)の表示用文字列

my $update_lock = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::check_lockfile($update_lock,$ENV{REMOTE_ADDR},\$other_user) ){	# データ更新中は使用不可
  require '../common/http_header.pm';
  print &TMSlock::data_updating_page( $other_user );
  exit;
}

# 各ファイル名の取得
my $xlsfile = "../xlsfile/$lang/statushistory.xls";

my $datafile = &TMScommon::get_xlsdata_file_name("statushistory","csv");

my $infofile = "statushistory.tmshlp";


# ＣＳＶファイルの出力
open(OUT, "> $datafile" );

my $now_date = &TMScommon::get_now_date();

print OUT	"( $now_date )\n".
		"$index[0] -> $index[$#index]\n".
		"\n";

print OUT &make_statushistory_title( $period,
                                     &TMSselitem::is_jat_ari(),
                                     &TMSselitem::is_lwt_ari() );

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
      print OUT &make_statushistory_data( $index[$i], \$line );
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

sub make_statushistory_title
{
  my ( $period, $jat_ari, $lwt_ari ) = @_;

  #### Data Parameter ####

  my $period_type = 0;

  ########################

  my $line =	"";
  if(    $period eq "shift" ){ $period_type = 0; $line .= "SHIFT"; }
  elsif( $period eq "date"  ){ $period_type = 1; $line .= "DATE";  }
  elsif( $period eq "week"  ){ $period_type = 2; $line .= "WEEK";  }
  elsif( $period eq "month" ){ $period_type = 3; $line .= "MONTH"; }

  $line .=	",LOOM,STYLE".
		",EFFIC&PERCENT,RUN&MINUTE,STOP&MINUTE".
		",WARP&COUNT,WARP_RATE&CPH,WARP_RATE&CPDAY,WEFT&COUNT,WEFT_RATE&CPH,WEFT_RATE&CPDAY";

  my $param_key = "PARAM->,period_type,jat_ari,lwt_ari";
  my $param_val = "VALUE->,$period_type,$jat_ari,$lwt_ari";

  return $param_key."\n".
	 $param_val."\n".
	 "\n".
	 $line."\n";
}


###################################################################################################

sub make_statushistory_data
{
  my ( $index, $r_line ) = @_;
 
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
  my $run_tm     = $tmp{"run_tm"};
  my $stop_ttm   = $tmp{"stop_ttm"};
  my @stop_ct    = split(/ /,$tmp{"stop_ct"});

  # Ver3.0以前の旧データ対応
  if( $#stop_ct < 11 ){ $stop_ct[11] = 0; }  # CC後

  #my $warp_ct = $stop_ct[0] + $stop_ct[1];
  #my $weft_ct = $stop_ct[2] + $stop_ct[3] + $stop_ct[4] + $stop_ct[5];

  # 仕様間違い修正+CC後追加(Ver3.0～)
  my $warp_ct = $stop_ct[0] + $stop_ct[1] + $stop_ct[2] + $stop_ct[3] + $stop_ct[4] + $stop_ct[11];
  my $weft_ct = $stop_ct[5];

  #### Create CSV Data ####

  my $htdata = 	"$index".
		",=\"$mac_name\"".
		",=\"$style_name\"".
		",".		# effic
		",$run_tm".
		",$stop_ttm".
		",$warp_ct".
		",,".		# Warp Stop Rate
		",$weft_ct".
		",,".		# Weft Stop Rate
		"\n";
 return $htdata;
}

###################################################################################################
