
import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  CircularProgress,
  Chip,
  Divider,
  LinearProgress,
} from "@material-ui/core";

import { makeStyles } from "@material-ui/core/styles";
import CloudUploadIcon from "@material-ui/icons/CloudUpload";
import EcoIcon from "@material-ui/icons/Eco";
import ImageIcon from "@material-ui/icons/Image";
import CheckCircleOutlineIcon from "@material-ui/icons/CheckCircleOutline";
import ClearIcon from "@material-ui/icons/Clear";

import backgroundImage from "./bg.png";

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const API_URL =
  process.env.REACT_APP_API_URL ||
  "http://127.0.0.1:8000/predict";

const POTATO_REJECTION_MESSAGE =
  "This image could not be confidently identified as a potato leaf. Please upload only potato leaf image.";

const useStyles = makeStyles((theme) => ({
  root: {
    minHeight: "100vh",
    backgroundColor: "#f5f8f4",
  },

  appBar: {
    backgroundColor: "#163c2b",
    boxShadow: "0 3px 16px rgba(20,45,30,.12)",
  },

  toolbar: {
    minHeight: 70,
    padding: "0 5%",
    [theme.breakpoints.down("xs")]: {
      padding: "0 16px",
    },
  },

  brandIcon: {
    color: "#a7d7a0",
    fontSize: 32,
    marginRight: 12,
  },


  brandTitle: {
    fontWeight: 800,
    fontSize: 28,
    letterSpacing: "0.3px",
    lineHeight: 1.25,
    "@media (max-width: 600px)": {
      fontSize: 23,
    },
  },


  brandSubtitle: {
    color: "#c4d9cb",
    fontSize: 11,
    letterSpacing: 1,
    textTransform: "uppercase",
  },

  statusChip: {
    color: "#e1f5e5",
    backgroundColor: "rgba(255,255,255,.12)",
    "& .MuiChip-icon": {
      color: "#a7d7a0",
    },
    [theme.breakpoints.down("xs")]: {
      display: "none",
    },
  },

  main: {
    minHeight: "calc(100vh - 70px)",
    padding: theme.spacing(5, 0, 3),
    backgroundImage: `
      linear-gradient(
        135deg,
        rgba(244,249,242,.97),
        rgba(235,244,232,.94)
      ),
      url(${backgroundImage})
    `,
    backgroundSize: "cover",
    backgroundPosition: "center",
    [theme.breakpoints.down("xs")]: {
      paddingTop: theme.spacing(3),
    },
  },

  hero: {
    textAlign: "center",
    maxWidth: 740,
    margin: "0 auto",
    padding: theme.spacing(1, 2, 4),
  },

  eyebrow: {
    display: "inline-flex",
    alignItems: "center",
    gap: 7,
    padding: "7px 14px",
    borderRadius: 30,
    backgroundColor: "#e4f0e2",
    color: "#286341",
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: ".6px",
    marginBottom: theme.spacing(2),
  },

  heroTitle: {
    color: "#183d2b",
    fontWeight: 800,
    fontSize: 42,
    lineHeight: 1.2,
    letterSpacing: "-1px",
    marginBottom: theme.spacing(2),
    [theme.breakpoints.down("xs")]: {
      fontSize: 30,
    },
  },

  highlight: {
    color: "#39834d",
  },

  description: {
    maxWidth: 620,
    margin: "0 auto",
    color: "#627267",
    fontSize: 15,
    lineHeight: 1.8,
  },

  card: {
    maxWidth: 850,
    margin: "0 auto",
    borderRadius: 20,
    overflow: "hidden",
    border: "1px solid #e2eae0",
    boxShadow: "0 15px 45px rgba(35,72,43,.09)",
  },

  cardHeader: {
    padding: theme.spacing(3),
    [theme.breakpoints.down("xs")]: {
      padding: theme.spacing(2),
    },
  },

  sectionTitle: {
    color: "#203e2d",
    fontSize: 20,
    fontWeight: 700,
  },

  mutedText: {
    color: "#7b887d",
    fontSize: 13,
    marginTop: 6,
    lineHeight: 1.6,
  },

  cardBody: {
    padding: theme.spacing(3),
    [theme.breakpoints.down("xs")]: {
      padding: theme.spacing(2),
    },
  },

  dropArea: {
    minHeight: 270,
    padding: theme.spacing(4, 2),
    border: "2px dashed #a9c9a8",
    borderRadius: 16,
    backgroundColor: "#f8fbf7",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    textAlign: "center",
    cursor: "pointer",
    transition: "background-color .2s, border-color .2s",
    outline: "none",
    "&:hover, &:focus-visible": {
      backgroundColor: "#edf6eb",
      borderColor: "#438454",
    },
  },

  dragActive: {
    backgroundColor: "#e8f5e5",
    borderColor: "#39834d",
  },

  uploadIconCircle: {
    height: 68,
    width: 68,
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#e3f0df",
    color: "#39834d",
    marginBottom: theme.spacing(2),
  },

  uploadIcon: {
    fontSize: 34,
  },

  uploadTitle: {
    fontSize: 18,
    fontWeight: 700,
    color: "#244831",
  },

  browseButton: {
    marginTop: theme.spacing(2),
    padding: "10px 23px",
    borderRadius: 10,
    backgroundColor: "#286341",
    color: "#fff",
    textTransform: "none",
    fontWeight: 700,
    "&:hover": {
      backgroundColor: "#1b4c30",
    },
  },

  helperText: {
    fontSize: 12,
    color: "#7b887d",
    marginTop: theme.spacing(2),
  },

  hiddenInput: {
    display: "none",
  },

  previewPanel: {
    padding: 12,
    border: "1px solid #e3eae1",
    borderRadius: 15,
    backgroundColor: "#fafcf9",
  },

  preview: {
    display: "block",
    width: "100%",
    maxHeight: 390,
    objectFit: "contain",
    borderRadius: 10,
    backgroundColor: "#f0f3ee",
  },

  imageName: {
    fontSize: 12,
    color: "#718075",
    marginTop: 10,
    textAlign: "center",
    overflowWrap: "anywhere",
  },

  processing: {
    textAlign: "center",
    padding: theme.spacing(3, 1),
    color: "#42644b",
  },

  loader: {
    color: "#39834d",
    marginBottom: 12,
  },

  result: {
    marginTop: theme.spacing(3),
    padding: theme.spacing(2.5),
    backgroundColor: "#f2f8f0",
    border: "1px solid #dcebd8",
    borderRadius: 14,
  },

  resultLabel: {
    fontSize: 12,
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: ".7px",
    color: "#6a806d",
    marginBottom: 8,
  },

  resultValue: {
    fontSize: 22,
    fontWeight: 800,
    color: "#245d35",
    overflowWrap: "anywhere",
  },

  progress: {
    height: 8,
    borderRadius: 8,
    marginTop: 12,
    backgroundColor: "#dcebd8",
    "& .MuiLinearProgress-bar": {
      backgroundColor: "#39834d",
    },
  },

  error: {
    marginTop: theme.spacing(2),
    padding: theme.spacing(2),
    borderRadius: 12,
    color: "#a43d30",
    backgroundColor: "#fff3f0",
    border: "1px solid #f0d0ca",
    overflowWrap: "anywhere",
  },

  actionRow: {
    display: "flex",
    justifyContent: "center",
    marginTop: theme.spacing(2),
  },

  clearButton: {
    textTransform: "none",
    fontWeight: 700,
    padding: "10px 22px",
    borderRadius: 10,
    borderColor: "#cad9ca",
    color: "#355c40",
  },

  footer: {
    textAlign: "center",
    padding: theme.spacing(3, 1, 0),
    color: "#7d8c7e",
    fontSize: 12,
  },
}));

export const ImageUpload = () => {
  const classes = useStyles();
  const inputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);

  // Create and clean up the selected image preview URL.
  useEffect(() => {
    if (!selectedFile) {
      setPreview(null);
      return undefined;
    }

    const objectUrl = URL.createObjectURL(selectedFile);
    setPreview(objectUrl);

    return () => URL.revokeObjectURL(objectUrl);
  }, [selectedFile]);

  // Send the selected image to the FastAPI prediction endpoint.
  useEffect(() => {
    if (!selectedFile) return undefined;

    const controller = new AbortController();

    const predict = async () => {
      setIsLoading(true);
      setData(null);
      setError("");

      try {
        const formData = new FormData();
        formData.append("file", selectedFile);

        const response = await axios.post(API_URL, formData, {
          signal: controller.signal,
        });

        if (!response.data || typeof response.data !== "object") {
          throw new Error("The prediction API returned an unexpected response.");
        }

        if (!response.data.class) {
          throw new Error("The API response does not contain a predicted class.");
        }

        setData(response.data);
      } catch (err) {
        if (
          err.code === "ERR_CANCELED" ||
          err.name === "CanceledError" ||
          controller.signal.aborted
        ) {
          return;
        }

        console.error("Prediction failed:", err);

        const responseData = err.response?.data;

        let errorMessage =
          typeof responseData === "string"
            ? responseData
            : responseData?.detail ||
              responseData?.message ||
              err.message ||
              "Prediction failed. Check the backend and try again.";

        // Support the custom potato-leaf rejection response.
        if (
          typeof errorMessage === "string" &&
          errorMessage.includes("could not be confidently identified")
        ) {
          errorMessage = POTATO_REJECTION_MESSAGE;
        }

        if (err.response?.status === 413) {
          errorMessage = "The image exceeds the 10 MB upload limit.";
        } else if (
          !err.response &&
          !controller.signal.aborted
        ) {
          errorMessage =
            "Cannot connect to the prediction API. Make sure the backend is running.";
        }

        setError(errorMessage);
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    };

    predict();

    return () => controller.abort();
  }, [selectedFile]);

  // Validate the selected file before sending it to the API.
  const chooseFile = (file) => {
    setError("");
    setData(null);

    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setError("Please select an image file such as JPG, PNG, or WEBP.");
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError("The image must be smaller than 10 MB.");
      return;
    }

    setSelectedFile(file);
  };

  const handleInputChange = (event) => {
    const file = event.target.files && event.target.files[0];
    chooseFile(file);

    // Allow the same image to be selected again.
    event.target.value = "";
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);

    const file =
      event.dataTransfer.files &&
      event.dataTransfer.files[0];

    chooseFile(file);
  };

  const clearData = () => {
    setSelectedFile(null);
    setData(null);
    setError("");
    setIsLoading(false);
    setIsDragging(false);

    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  const confidence = (() => {
    if (data?.confidence === undefined || data?.confidence === null) {
      return null;
    }

    const value = Number(data.confidence);

    if (!Number.isFinite(value)) return null;

    const percentage =
      value >= 0 && value <= 1 ? value * 100 : value;

    return Math.max(0, Math.min(100, percentage));
  })();

  const potatoProbability = (() => {
    if (
      data?.potato_leaf_probability === undefined ||
      data?.potato_leaf_probability === null
    ) {
      return null;
    }

    const value = Number(data.potato_leaf_probability);

    if (!Number.isFinite(value)) return null;

    const percentage =
      value >= 0 && value <= 1 ? value * 100 : value;

    return Math.max(0, Math.min(100, percentage));
  })();

  return (
    <div className={classes.root}>
      <AppBar position="static" className={classes.appBar}>
        <Toolbar className={classes.toolbar}>
          <EcoIcon className={classes.brandIcon} />

          <Box>
            <Typography className={classes.brandTitle}>
              PotatoGuard AI
            </Typography>

            <Typography className={classes.brandSubtitle}>
              Smart crop health analysis
            </Typography>
          </Box>

          <Box flexGrow={1} />

          <Chip
            className={classes.statusChip}
            size="small"
            icon={<CheckCircleOutlineIcon />}
            label="AI-powered detection"
          />
        </Toolbar>
      </AppBar>

      <main className={classes.main}>
        <Container maxWidth="md">
          <section className={classes.hero}>
            <div className={classes.eyebrow}>
              <EcoIcon style={{ fontSize: 17 }} />
              INTELLIGENT PLANT HEALTH
            </div>

            <Typography component="h1" className={classes.heroTitle}>
              Protect your crops with{" "}
              <span className={classes.highlight}>AI insights</span>
            </Typography>

            <Typography className={classes.description}>
              Upload a potato leaf image to analyze its condition using
              a deep learning model. View the predicted disease class
              and confidence score.
            </Typography>
          </section>

          <Card className={classes.card} elevation={0}>
            <CardContent className={classes.cardHeader}>
              <Typography className={classes.sectionTitle}>
                Leaf disease detector
              </Typography>

              <Typography className={classes.mutedText}>
                Upload a clear potato leaf photo to begin the analysis.
              </Typography>
            </CardContent>

            <Divider />

            <CardContent className={classes.cardBody}>
              <input
                ref={inputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp,image/bmp"
                className={classes.hiddenInput}
                onChange={handleInputChange}
              />

              {!selectedFile && (
                <div
                  className={`${classes.dropArea} ${
                    isDragging ? classes.dragActive : ""
                  }`}
                  role="button"
                  tabIndex={0}
                  aria-label="Upload a potato leaf image"
                  onClick={() => inputRef.current?.click()}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      inputRef.current?.click();
                    }
                  }}
                  onDragOver={(event) => {
                    event.preventDefault();
                    setIsDragging(true);
                  }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={handleDrop}
                >
                  <div className={classes.uploadIconCircle}>
                    <CloudUploadIcon className={classes.uploadIcon} />
                  </div>

                  <Typography className={classes.uploadTitle}>
                    Drag and drop your image here
                  </Typography>

                  <Typography className={classes.mutedText}>
                    or browse files from your computer
                  </Typography>

                  <Button
                    variant="contained"
                    className={classes.browseButton}
                    startIcon={<ImageIcon />}
                    onClick={(event) => {
                      event.stopPropagation();
                      inputRef.current?.click();
                    }}
                  >
                    Choose leaf image
                  </Button>

                  <Typography className={classes.helperText}>
                    JPG, PNG, WEBP or BMP · Maximum size 10 MB
                  </Typography>
                </div>
              )}

              {selectedFile && preview && (
                <div className={classes.previewPanel}>
                  <img
                    src={preview}
                    alt="Selected image for potato leaf analysis"
                    className={classes.preview}
                  />

                  <Typography className={classes.imageName}>
                    {selectedFile.name}
                  </Typography>
                </div>
              )}

              {isLoading && (
                <div className={classes.processing}>
                  <CircularProgress
                    size={36}
                    className={classes.loader}
                  />

                  <Typography variant="body1">
                    Analyzing image...
                  </Typography>

                  <Typography variant="body2" color="textSecondary">
                    Please wait while the model processes your image.
                  </Typography>
                </div>
              )}

              {data && !error && (
                <div className={classes.result}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={7}>
                      <Typography className={classes.resultLabel}>
                        Predicted condition
                      </Typography>

                      <Typography className={classes.resultValue}>
                        {data.class || "Prediction unavailable"}
                      </Typography>
                    </Grid>

                    {confidence !== null && (
                      <Grid item xs={12} sm={5}>
                        <Typography className={classes.resultLabel}>
                          Model confidence
                        </Typography>

                        <Typography className={classes.resultValue}>
                          {confidence.toFixed(2)}%
                        </Typography>

                        <LinearProgress
                          variant="determinate"
                          value={confidence}
                          className={classes.progress}
                        />
                      </Grid>
                    )}

                    {potatoProbability !== null && (
                      <Grid item xs={12}>
                        <Typography className={classes.resultLabel}>
                          Potato leaf probability
                        </Typography>

                        <Typography className={classes.resultValue}>
                          {potatoProbability.toFixed(2)}%
                        </Typography>

                        <LinearProgress
                          variant="determinate"
                          value={potatoProbability}
                          className={classes.progress}
                        />
                      </Grid>
                    )}
                  </Grid>

                  <Typography
                    variant="body2"
                    style={{
                      color: "#647565",
                      marginTop: 18,
                      lineHeight: 1.7,
                    }}
                  >
                    This is an AI model prediction, not a confirmed
                    diagnosis. Images outside the model's training
                    domain may produce unreliable results.
                  </Typography>
                </div>
              )}

              {error && (
                <div className={classes.error} role="alert">
                  <Typography variant="subtitle2">
                    Unable to analyze the image
                  </Typography>

                  <Typography
                    variant="body2"
                    style={{ marginTop: 5 }}
                  >
                    {error}
                  </Typography>
                </div>
              )}

              {selectedFile && !isLoading && (
                <Box
                  display="flex"
                  justifyContent="center"
                  mt={2}
                >
                  <Button
                    variant="outlined"
                    className={classes.clearButton}
                    startIcon={<ClearIcon />}
                    onClick={clearData}
                  >
                    Upload another image
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>

          <footer className={classes.footer}>
            <EcoIcon
              style={{
                fontSize: 15,
                verticalAlign: "middle",
                marginRight: 5,
                color: "#51815a",
              }}
            />
            Potato Disease Classification · AI-assisted crop analysis
          </footer>
        </Container>
      </main>
    </div>
  );
};
