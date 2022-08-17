class TemplateConst:
    MAIN_CONTENT = '''{
	Tools = ordered() {
		PSDOBJ = GroupOperator {
			Inputs = ordered() {%%%INPUT_CONTENT%%%
			},
			Outputs = {
				MainOutput1 = InstanceOutput {
					SourceOp = "MediaOut1",
					Source = "Output",
				}
			},
			ViewInfo = GroupInfo { Pos = { 0, 0 } },
			Tools = ordered() {
				%%%LOADER_CONTENT%%%
                %%%BACKGROUND_CONTENT%%%
				%%%MEDIAOUT_CONTENT%%%
                %%%MERGE_CONTENT%%%
			},
		}
	},
	ActiveTool = "PSDOBJ"
}'''

    INPUT_CONTENT_PARTS = '''
				%%%NODE_NAME%%% = InstanceInput {
					SourceOp = "%%%SOURCE_NAME%%%",
					Source = "image_selector",
					},'''
    INPUT_CONTENT_GROUP_PARTS = '''
				%%%NODE_NAME%%% = InstanceInput {
					SourceOp = "Background1",
					Source = "%%%SOURCE_GROUP_NAME%%%",
					},'''

    LOADER_CONTENT_PARTS = '''
                    %%%NODE_NAME%%% = Loader {
    					Clips = {
    						Clip {
    							ID = "%%%CLIP_ID%%%",
    							Filename = "%%%CLIP_FILE_PATH%%%",
    							FormatID = "PNGFormat",
    							StartFrame = %%%CLIP_START_FRAME%%%,
    							Length = %%%CLIP_LENGTH%%%,
    							LengthSetManually = true,
    							TrimIn = 0,
    							TrimOut = 0,
    							ExtendFirst = 0,
    							ExtendLast = 0,
    							Loop = 0,
    							AspectMode = 0,
    							Depth = 0,
    							TimeCode = 0,
    							GlobalStart = 0,
    							GlobalEnd = 0
    						}
    					},
    					Inputs = {
    						["Gamut.ColorSpaceNest"] = Input { Value = 1, },
    						["Gamut.GammaSpaceNest"] = Input { Value = 1, },
    						["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
    						["%%%CLIP_ID%%%.PNGFormat.PostMultiply"] = Input { Value = 1, },
    						Comments = Input { Value = "%%%SCRIPT_COMMENT%%%", },
    						FrameRenderScript = Input { Value = "%%%FRAMERANDER_SCRIPT%%%", },
    						StartRenderScripts = Input { Value = 1, },
    						StartRenderScript = Input { Value = "%%%STARTRENDER_SCRIPT%%%", },
							image_selector = Input { Value = %%%IMAGE_SELECTOR_SELECT%%%, },
    					},
    					ViewInfo = OperatorInfo { Pos = { %%%NODE_POS_X%%%, %%%NODE_POS_Y%%% } },
    					UserControls = ordered() {
    						image_selector = {
    							LINKS_Name = "%%%LAYER_GROUP_NAME%%%",
    							LINKID_DataType = "Number",
    							INPID_InputControl = "ComboControl",
    							INP_Integer = false,
    							INP_MinScale = 0,
    							INP_MaxScale = %%%MAX_NUM_LENGTH%%%,
    							INP_MinAllowed = -1000000,
    							INP_MaxAllowed = 1000000,
%%%CSS_ADD_STRING_LIST%%%
    							CC_LabelPosition = "Horizontal",
    						}
    					}
    				},'''

    BACKGROUND_CONTENT = '''
                    Background1 = Background {
    					Inputs = {
    						Width = Input { Value = %%%SIZE_WIDTH%%%, },
    						Height = Input { Value = %%%SIZE_HEIGHT%%%, },
    						["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
							TopLeftAlpha = Input { Value = 0, },
    					},
    					ViewInfo = OperatorInfo { Pos = { %%%NODE_POS_X%%%, %%%NODE_POS_Y%%% } },
           					UserControls = ordered() {%%%LABEL_CONTENT%%%
						},
    				},'''
        
    BACKGROUND_LABEL_CONTENT_PARTS = '''
    							%%%GROUP_LABEL_NAME%%% = {
								LINKS_Name = "%%%LAYER_PARENT_GROUP_NAME%%%",
								LINKID_DataType = "Number",
								INPID_InputControl = "LabelControl",
								INP_Integer = false,
								LBLC_DropDownButton = true,
								LBLC_NumInputs = %%%LAYER_PARENT_NUM_INPUTS%%%,
							},'''

    MERGE_CONTENT_PARTS = '''
    				%%%NODE_NAME%%% = Merge {
    					Inputs = {
    						Background = Input {
    							SourceOp = "%%%BACKGROUND_SOURCE%%%",
    							Source = "Output",
    						},
    						Foreground = Input {
    							SourceOp = "%%%FOREGROUND_SOURCE%%%",
    							Source = "Output",
    						},
    						Center = Input { Value = { 1, 1 }, },
    						PerformDepthMerge = Input { Value = 0, },
							ReferenceSize = Input { Value = 1, },
    					},
    					ViewInfo = OperatorInfo { Pos = { %%%NODE_POS_X%%%, %%%NODE_POS_Y%%% } },
    				},'''
        
    OUTPUT_CONTENT = '''
     			MediaOut1 = MediaOut {
					Inputs = {
						Index = Input { Value = "0", },
						Input = Input {
							SourceOp = "%%%SOURCE_OP%%%",
							Source = "Output",
						},
					},
					ViewInfo = OperatorInfo { Pos = { %%%NODE_POS_X%%%, %%%NODE_POS_Y%%% } },
				},'''