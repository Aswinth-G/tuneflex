\# System Architecture – TuneFlex



\## High-Level Architecture



Frontend / Mobile App

&nbsp;       |

&nbsp;       | REST API

&nbsp;       v

Backend (FastAPI - Python)

&nbsp;       |

&nbsp;       |----------------------------

&nbsp;       |            |              |

Music Search   Image Detection   Singing Generator

Engine         (YOLO + OCR)      (DiffSinger)

&nbsp;       |

Local Database (Metadata)

&nbsp;       |

Local Audio Storage (.wav files)



\## Architecture Style

\- Client–Server Architecture

\- REST-based communication

\- Offline-first design



