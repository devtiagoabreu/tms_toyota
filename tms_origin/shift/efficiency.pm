###################################################################################################
# efficiency.pm
###################################################################################################

use strict;

###################################################################################################

sub make_efficiency_title
{
  my ($mode, $period, $jat_ari, $lwt_ari) = @_;

  #### Data Parameter ####

  my $data_type   = 0;
  my $period_type = 0;

  ########################

  my $line = "";
  if(    $period eq "shift" ){ $period_type = 0; $line .= "SHIFT"; }
  elsif( $period eq "date"  ){ $period_type = 1; $line .= "DATE";  }
  elsif( $period eq "week"  ){ $period_type = 2; $line .= "WEEK";  }
  elsif( $period eq "month" ){ $period_type = 3; $line .= "MONTH"; }

  if( $mode eq "shift" ){
    $data_type = 0;
  }
  else{ # "operator"
    $data_type = 1;
    $line .=	",OPERATOR";
  }

  $line .=	",LOOM,STYLE".
		",EFFIC&PERCENT,RUN&MINUTE,STOP&MINUTE,".
		"WARP&COUNT,WARP_RATE&CPH,WARP_RATE&CPDAY,WEFT&COUNT,WEFT_RATE&CPH,WEFT_RATE&CPDAY";

  my $param_key = "PARAM->,data_type,period_type,jat_ari,lwt_ari";
  my $param_val = "VALUE->,$data_type,$period_type,$jat_ari,$lwt_ari";

  return $param_key."\n".
	 $param_val."\n".
	 "\n".
	 $line."\n";
}

###################################################################################################

sub make_efficiency_data
{
  my ( $mode, $index, $r_line ) = @_;

  $$r_line =~ s/\n$//;		# 改行コードを削除。
# $$r_line =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
  my @list = split(/,/,$$r_line);

  my %tmp = ();
  foreach(@list){
    my @data = split(/ /,$_,2);
    if( $#data >= 1 ){ $tmp{$data[0]} = $data[1]; }
  }

  my $mac_name = $tmp{"mac_name"};
  my $ope_name = "";
  if( $mode eq "operator" ){ $ope_name = $tmp{"ope_name"}; }
  my $style    = $tmp{"style"};
  my $run_tm   = $tmp{"run_tm"};
  my $stop_ttm = $tmp{"stop_ttm"};
  my @stop_ct  = split(/ /,$tmp{"stop_ct"});

  # Ver3.0以前の旧データ対応
  if( $#stop_ct < 11 ){ $stop_ct[11] = 0; }  # CC後

  #my $warp_ct = $stop_ct[0] + $stop_ct[1];
  #my $weft_ct = $stop_ct[2] + $stop_ct[3] + $stop_ct[4] + $stop_ct[5];

  # 仕様間違い修正+CC後追加(Ver3.0～)
  my $warp_ct = $stop_ct[0] + $stop_ct[1] + $stop_ct[2] + $stop_ct[3] + $stop_ct[4] + $stop_ct[11];
  my $weft_ct = $stop_ct[5];

  #### Create CSV Data ####

  my $htdata =	"$index";

  if( $mode eq "operator" ){ $htdata .= ",=\"$ope_name\""; }

  $htdata .=	",=\"$mac_name\"".
		",=\"$style\"".
		",".		# Efficiency
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
1;
