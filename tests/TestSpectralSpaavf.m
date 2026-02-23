classdef TestSpectralSpaavf < matlab.unittest.TestCase
    properties
        RepoRoot
    end

    methods (TestMethodSetup)
        function addToolboxToPath(testCase)
            testCase.RepoRoot = fileparts(fileparts(mfilename('fullpath')));
            addpath(testCase.RepoRoot);
        end
    end

    methods (TestMethodTeardown)
        function removeToolboxFromPath(testCase)
            rmpath(testCase.RepoRoot);
        end
    end

    methods (Test)
        function spaavfOpenLoopRunsAndReturnsFinite(testCase)
            [u, y, ~] = testutils.makeSisoData('N', 512 ,'seed', 20, 'noiseStd', 0.02);

            dt = 1;
            Nband = 4;
            Nfft = 256;

            % Open-loop call style: spaavf(u, y, Ts, Nband, Nfft)
            [G, w] = spaavf(u, y, dt, Nband, Nfft);

            testCase.verifyTrue(all(isfinite(w)));
            testCase.verifyGreaterThan(numel(w), 0);

            % For open-loop SISO: G is 1x1xN
            testCase.verifyEqual(size(G,1), 1);
            testCase.verifyEqual(size(G,2), 1);
            testCase.verifyEqual(size(G,3), numel(w));
            testCase.verifyTrue(all(isfinite(G(:))));

            % Frequencies should be within [0, pi/dt]
            testCase.verifyGreaterThanOrEqual(min(w), -1e-12);
            testCase.verifyLessThanOrEqual(max(w), pi/dt + 1e-8);
        end

        function spaavfClosedLoopCallStyleRuns(testCase)
            % Closed-loop call style: spaavf(u, y, r, Ts, Nband, ...)
            N = 512;
            rng(21, 'twister');

            dt = 1;
            Nband = 4;
            Nfft = 256;

            r = randn(N,1);

            % Make u strongly correlated with r (non a real closed-loop, but triggers clmode)
            u = r + 0.1*randn(N,1);

             % Create y from a stable first-order system driven by u
            y = zeros(N,1);

            for k = 2:N
                y(k) = 0.7*y(k-1) + 0.2*u(k-1) + 0.02*randn();
            end

            [G, w] = spaavf(u, y, r, dt, Nband, Nfft);

            testCase.verifyTrue(all(isfinite(w)));
            testCase.verifyGreaterThan(numel(w), 0);

            % Closed-loop branch returns ny x nr x Nmod. Here SISO, so 1x1xN
            testCase.verifyEqual(size(G, 1), 1)
            testCase.verifyEqual(size(G, 2), 1)
            testCase.verifyEqual(size(G, 3), numel(w));
            testCase.verifyTrue(all(isfinite(G(:))));
        end
    end
end